# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
import logging
import argparse
from contextlib import closing
from datetime import datetime as dt
from datetime import timedelta
from matplotlib import axes
from matplotlib import pyplot
from matplotlib import dates 

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

logger = logging.getLogger(__name__)


class Grapher:
    def __init__(self, cfg: config.ConfigParser):
        self.cfg = cfg

    def create(self):
        # acquire the database
        with closing(sqlite3.connect(self.cfg.fp_database)) as database:
            # init graph
            fig, axs = pyplot.subplots(ncols=1, nrows=len(self.cfg.command_cfgs.values()), figsize=(7, 4))
            if isinstance(axs, axes.Axes):
                axs = [axs]
            # calc the reference time stamp
            current_time_stamp = dt.now()
            reference_time_stamp = (dt.now() - timedelta(hours=24))
            # acquire the cursor
            cursor = database.cursor()
            # create records for each server
            for ax, command_cfg in zip(axs, self.cfg.command_cfgs.values()):
                # data
                times = []
                values = []
                # create a table if it doesn't exist
                acquire = "SELECT * FROM \"{}\" WHERE {} <= time_stamp".format(command_cfg.name, reference_time_stamp.strftime("%s"))
                cursor.execute(acquire)
                rows = cursor.fetchall()
                for value, time_stamp in rows:
                    times.append(dt.fromtimestamp(time_stamp))
                    values.append(value)
                # plot
                ax.plot(times, values)
                # set title
                ax.set_title(command_cfg.name)
                # show grids
                ax.grid(True)
                # set range of x-axis
                ax.set_xlim([reference_time_stamp, current_time_stamp])
            # remove labels of x-axis except for last row
            for ax in axs[0:-1]:
                for tick in ax.get_xticklabels():
                    tick.set_visible(False)
            # rotate labels of x-axis of last row
            for tick in axs[-1].get_xticklabels():
                tick.set_rotation(15)
            # formatting labels of x-axis of last row
            xfmt = dates.DateFormatter("%m-%d %H:%M")
            axs[-1].xaxis.set_major_formatter(xfmt)
            # adjust
            pyplot.subplots_adjust(hspace=0.3)
            # save
            fig.savefig("graph.pdf", bbox_inches="tight", pad_inches=0.1)

    def send(self):
        pass


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="fp_cfg", metavar="CONFIG_FILE", help="config file path (config.yaml)", type=str)
    args = parser.parse_args()

    # parse the config file
    cfg = config.ConfigParser(args.fp_cfg)

    # create the graph(s)
    grapher = Grapher(cfg)
    grapher.create()
    grapher.send()
