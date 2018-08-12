# -*- coding: utf-8 -*-
import os
import sys
import sqlite3
import logging
import argparse
import subprocess
from contextlib import closing
from collections import namedtuple
from datetime import datetime as dt
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, cfg: config.ConfigParser):
        self.cfg = cfg

    def refresh(self):
        # acquire the database
        with closing(sqlite3.connect(self.cfg.fp_database)) as database:
            # acquire the cursor
            cursor = database.cursor()
            # create records for each server
            for command_cfg in self.cfg.command_cfgs.values():
                # create a table if it doesn't exist
                create_table = "CREATE TABLE IF NOT EXISTS \"{}\" (value FLOAT, time_stamp TIMESTAMP)".format(command_cfg.name)
                cursor.execute(create_table)

                # execute the command
                try:
                    ret = subprocess.check_output(command_cfg.command, shell=True)
                    value = float(ret)
                    time_stamp = dt.now().strftime("%s")
                    if value is not None:
                        logger.info("Executed the command '{}'.".format(command_cfg.command))
                        # insert the records
                        insert = "INSERT INTO \"{}\" (value, time_stamp) VALUES (?,?)".format(command_cfg.name)
                        cursor.execute(insert, [value, time_stamp])
                    else:
                        raise subprocess.CalledProcessError
                except subprocess.CalledProcessError as e:
                    logger.warning("Command '{}' has not been succeeded.".format(e.cmd))
                
                # delete the old records
                delete = "DELETE FROM \"{}\" WHERE time_stamp <= ?".format(command_cfg.name)
                outdated_time_stamp = (dt.now() - timedelta(days=30)).strftime('%s')
                cursor.execute(delete, [outdated_time_stamp])

                # commit the database
                database.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    
    parser = argparse.ArgumentParser()
    parser.add_argument(dest="fp_cfg", metavar="CONFIG_FILE", help="config file path (config.yaml)", type=str)
    args = parser.parse_args()

    # parse the config file
    cfg = config.ConfigParser(args.fp_cfg)

    # refresh the database
    database = Database(cfg)
    database.refresh()
