#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# getBalloonCfg -- function for reading INI file for Balloon variables                                         #
#                                                                                                              #
# Copyright (C) 2023 Mike Pate - K5MAP                                                                         #
#                                                                                                              #
# This program is free software; you can redistribute it and/or modify                                         #
# it under the terms of the GNU General Public License as published by                                         #
# the Free Software Foundation; either version 2 of the License, or                                            #
# (at your option) any later version.                                                                          #
#                                                                                                              #
# Reference https://www.pythonforbeginners.com/basics/convert-ini-file-to-dictionary-in-python                 #
#==============================================================================================================#
#
# if not already installled, use pip to install the following
#
#    pip install configupdater
#
#==============================================================================================================#

import sys
import logging
import argparse
from configupdater import ConfigUpdater
import configparser

from constants import CFG_FILE


def getBalloonCfg():
    parser = argparse.ArgumentParser()
    parser.add_argument("bCallSign", help="Enter Balloon Callsign with SSID")
    args = parser.parse_args()


    cfgUpdater = ConfigUpdater()
    cfgUpdater.read(CFG_FILE)
    cfg = cfgUpdater.to_dict()
    return cfg[args.bCallSign.upper()]

#==============================================================================================================#

def checkCfg(bCallsign):
    if 'uploadcallsign' not in bCallsign.keys():
        logging.error(f" *** Item 'uploadcallsign' was NOT found in CFG file" )
        sys.exit( "\n*** Missing CFG item, check log file ***" )
    if 'wsprcallsign' not in bCallsign.keys():
        logging.error(f" *** Item 'wsprcallsign' was NOT found in CFG file" )
        sys.exit( "\n*** Missing CFG item, check log file ***" )
    if 'ballooncallsign' not in bCallsign.keys():
        logging.error(f" *** Item 'ballooncallsign' was NOT found in CFG file" )
        sys.exit( "\n*** Missing CFG item, check log file ***" )
    if 'timeslot' not in bCallsign.keys():
        logging.error(f" *** Item 'timeslot' was NOT found in CFG file" )
        sys.exit( "\n*** Missing CFG item, check log file ***" )
    if 'tracker' not in bCallsign.keys():
        logging.error(f" *** Item 'tracker' was NOT found in CFG file" )
        sys.exit( "\n*** Missing CFG item, check log file ***" )
    if 'comment' not in bCallsign.keys():
        logging.error(f" *** Item 'comment' was NOT found in CFG file" )
        sys.exit( "\n*** Missing CFG item, check log file ***" )
    if 'uploadsite' not in bCallsign.keys():
        logging.error(f" *** Item 'uploadsite' was NOT found in CFG file" )
        sys.exit( "\n*** Missing CFG item, check log file ***" )
    if 'telemetryfile' not in bCallsign.keys():
        logging.error(f" *** Item 'telemetryfile' was NOT found in CFG file" )
        sys.exit( "\n*** Missing CFG item, check log file ***" )
    if 'ldatetime' not in bCallsign.keys():
        logging.error(f" *** Item 'ldatetime' was NOT found in CFG file" )
        sys.exit( "\n*** Missing CFG item, check log file ***" )
    return

#==============================================================================================================#

def putBalloonCfg(Balloon, lDateTime):
    # save last datetime to ini
    cfgUpdater = ConfigUpdater()
    cfgUpdater.read(CFG_FILE)
    cfgUpdater[Balloon]['ldatetime'].value = lDateTime
    cfgUpdater.update_file()    
    return

"""    
    config_obj = configparser.ConfigParser()
    config_obj.read(CFG_FILE)
    cSection = config_obj[Balloon]
    cSection["lDateTime"] = lDateTime
    with open(CFG_FILE, 'w') as configfile:
        config_obj.write(configfile)
    logging.info(' lDateTime has been updated in the config file')
"""
