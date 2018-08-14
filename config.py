# -*- coding: utf-8 -*-
import os
import sys
import yaml
import logging
from collections import namedtuple

logger = logging.getLogger(__name__)

command_cfg = namedtuple("command_cfg", ("name", "command"))
smtp_params = namedtuple("smtp_params", ("server_address",
                                         "server_port",
                                         "password",
                                         "from_address",
                                         "to_address",
                                         "subject",
                                         "body"))

class ConfigParser:
    def __init__(self, fp_cfg: str):
        # config file path
        self.fp_cfg = os.path.realpath(os.path.expanduser(fp_cfg))

        # check if the config file can be opened correctly
        try:
            with open(self.fp_cfg, "r") as fin:
                # check if the config file can be parsed as YAML
                try:
                    self.yaml = yaml.load(fin)
                except yaml.YAMLError as e:
                    logger.fatal("Couldn't parse the config file '{}' as YAML.".format(self.fp_cfg))
                    sys.exit(1)
                logger.info("The config file '{}' has been imported.".format(self.fp_cfg))
        except OSError as e:
            logger.fatal("Couldn't find the config file '{}'.".format(e.filename))
            sys.exit(1)

        if self.yaml is None:
            logger.fatal("The config file '{}' is not in YAML format.".format(self.fp_cfg))
            sys.exit(1)

        # command config dict
        self.command_cfgs = {}
        for cfg in self.yaml["command_cfgs"]:
            # check if the keys of the dict are exist
            try:
                self.command_cfgs[cfg["Name"]] = command_cfg(cfg["Name"], cfg["Command"])
            except KeyError as e:
                logger.fatal("Couldn't find the field {} in the config file. Will be terminated.".format(e))
                sys.exit(1)
        logger.info("Load the {} configuration(s) of the command(s) from the config file.".format(len(self.command_cfgs.keys())))

        # sqlite3 database
        self.fp_database = os.path.realpath(os.path.join(os.path.dirname(__file__), "database.sqlite3"))
        try:
            self.fp_database = os.path.join(os.path.dirname(self.fp_cfg), self.yaml["database"])
            self.fp_database = os.path.realpath(self.fp_database)
        except KeyError as e:
            logger.warning("Couldn't find the field {} in the config file. Use the default.".format(e))
        logger.info("The database path is set as '{}'.".format(self.fp_database))

        # SMTP parameters
        self.smtp_params = smtp_params(self.yaml["smtp.server_address"],
                                       self.yaml["smtp.server_port"],
                                       self.yaml["smtp.password"],
                                       self.yaml["smtp.from_address"],
                                       self.yaml["smtp.to_address"],
                                       self.yaml["smtp.subject"],
                                       self.yaml["smtp.body"])
