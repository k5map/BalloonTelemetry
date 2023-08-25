#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# getQRPLabs                                                                                                   #
#                                                                                                              #
# Copyright (C) 2023 Mike Pate - K5MAP                                                                         #
#                                                                                                              #
# This program is free software; you can redistribute it and/or modify                                         #
# it under the terms of the GNU General Public License as published by                                         #
# the Free Software Foundation; either version 2 of the License, or                                            #
# (at your option) any later version.                                                                          #
#                                                                                                              #
# This program is distributed in the hope that it will be useful,                                              #
# but WITHOUT ANY WARRANTY; without even the implied warranty of                                               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                                #
# GNU General Public License for more details.                                                                 #
#                                                                                                              #
# You should have received a copy of the GNU General Public License along                                      #
# with this program; if not, write to the Free Software Foundation, Inc.,                                      #
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.                                                  #
#                                                                                                              #
#==============================================================================================================#
#
# if not already installled, use pip to install the following
#
#    pip install urllib3
#    pip install pprint
#
#==============================================================================================================#
#  Resources
#       Github for Zachtek tracker:  https://github.com/HarrydeBug/WSPR-transmitters/ 
#==============================================================================================================#

import logging
import traceback
import urllib.request, urllib.error
import json
from socket import *
from typing import Dict, List, Tuple
import pprint

from miscFunctions import *
from constants import __version__, SOFTWARE_NAME

#--------------------------------------------------------------------------------------------------------------#

def getQRPLabs(bCfg: Dict, last_date: str):
    """
    Function to retrieve WSPR records, create data structure and then upload to APRS-IS or SondeHub

    : param bCfg: dict, last_date: string (YYYY-MM-DD HH:MM:SS)
    : return: integer, dict, string
    """
    logging.info("#" + ("-"*130))
    logging.info(" Function AB5SS start" )

    # CFG values used in function
    wCallsign = bCfg['wsprcallsign']
    BalloonCallsign = bCfg['ballooncallsign']
    channel = bCfg['channel']
    timeslot = bCfg['timeslot']
    band = bCfg['band']

    query = "SELECT * FROM rx WHERE tx_sign='" + wCallsign + "' AND time > '" + last_date + "' ORDER BY time"
    logging.info(" SQL query = " + query )

    url = "https://db1.wspr.live/?query=" + urllib.parse.quote_plus(query + " FORMAT JSON")

    # download contents from wspr.live
    try:
        contents = urllib.request.urlopen(url).read()
    except urllib.error.URLError as erru:
        logging.critical(f" URL error - {erru.reason}" )
        return -1, None, None
    except urllib.error.HTTPError as errh:
        logging.critical(f" HTTP error - {errh}" )
        return -1, None, None
    except socket.timeout as errt:
        logging.critical(f" Connection timeout - {errt}" )
        return -1, None, None
    except:
        logging.critical(f" Unexpected error calling URL - {traceback.format_exc()}" )
        return -1, None, None

    # check on how many rows returned
    jWsprData = json.loads(contents.decode("UTF-8"))["data"]
    record_count = len(jWsprData)
    logging.info(f" WSPR Live records downloaded = {record_count}" )
    if record_count < 1:
        logging.warning(" Exit function, insufficient WSPR records to process" )
        return 0, None, None

    # eliminate duplicates
    jWsprData = deldupWspr(jWsprData)
    logging.info(f" WSPR Live records after removing duplicates = {len(jWsprData)}" )

    return
