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

import logging
import configparser
import argparse
#from configupdater import ConfigUpdater


def getBalloonCfg():
    cfgFile = "BalloonTelemetry.cfg"
    parser = argparse.ArgumentParser()
    parser.add_argument("bCallSign", help="Enter Balloon Callsign with SSID")
    args = parser.parse_args()

    config_object = configparser.ConfigParser()
    file = open(cfgFile, "r")
    config_object.read_file(file)
    output_dict = dict()
    sections = config_object.sections()
    for section in sections:
        items = config_object.items(section)
        output_dict[section] = dict(items)

    return output_dict[args.bCallSign.upper()]


#==============================================================================================================#

def putBalloonCfg(Balloon, lDateTime):
    # save last datetime to ini
    cfgFile = "BalloonTelemetry.cfg"
    config_obj = configparser.ConfigParser()
    config_obj.read(cfgFile)
    cSection = config_obj[Balloon]
    cSection["lDateTime"] = lDateTime
    with open(cfgFile, 'w') as configfile:
        config_obj.write(configfile)
    logging.info(' lDateTime has been updated in the config file')
    return
