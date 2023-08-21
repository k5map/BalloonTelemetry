#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# putAprsIS                                                                                                    #
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
#    pip install aprslib
#
#==============================================================================================================#
#  Resources
#       website for passcode - https://apps.magicbug.co.uk/passcode/
#       Website which explains APRS packet format - http://www.aprs.net/vm/DOS/PROTOCOL.HTM 
#       https://hugosprojects.wordpress.com/2014/03/20/implementing-aprs-gps-data/ 
#       APRS Telemetry - http://www.aprs.net/vm/DOS/TELEMTRY.HTM 
#       APRS symbols - http://www.aprs.net/vm/DOS/SYMBOLS.HTM (balloon is the letter O)
#       http://www.aprs.org/APRS-docs/PROTOCOL.TXT
#       K5WH-117>APRS,TCPIP*,qAS,W5MOM:/302315z3038.46N/13142.29EO000/000/A=056105 17100 K5WH-117 PM50up BVARC Brazos Valley ARC Field Day, STX BLT 1163
#       lat/lon - decimal to radian     https://github.com/ampledata/aprs/blob/master/aprs/decimaldegrees.py
#       time = 121234z  (12th day at 1234 military time)
#==============================================================================================================#

import logging
import traceback
import aprslib
import datetime
#import pprint
import math
from typing import Dict, List

from miscFunctions import *


def putAprsIS(wCallsign: str, jUploadData: List) -> int:
    logging.info("#" + ("-"*130))
    logging.info(" Function putAprsIS start" )

    #pprint.pp(jUploadData)

    i = len(jUploadData) - 1

    bCallsign = jUploadData[i]['payload_callsign']
    uCallsign = jUploadData[i]['uploader_callsign']
    passCode = getPassCode(uCallsign)

    # build raw_timestamp 
    t1 = datetime.datetime.strptime(jUploadData[i]['time_received'], "%Y-%m-%dT%H:%M:%S.%fZ")
    ztime = t1.strftime("%d%H%Mz")


    # lat / lon
    lat = deg_to_dms(jUploadData[i]['lat'], 'lat')
    lon = deg_to_dms(jUploadData[i]['lon'], 'lon')

    # calc atitude (feet)
    alt_ft = round(jUploadData[i]['alt'] * 3.281)
    alt = f'{alt_ft:06}'

    # build comment field
    # case statement for tracker value to determine how to build comment  !!!!!!!!!!!!!!!!!!!!
    comments = f" {jUploadData[i]['alt']} {wCallsign} {jUploadData[i]['grid']} {jUploadData[i]['comment']}"

    # build packet string
    packet = bCallsign + ">APRS,TCPIP*,qAS," + uCallsign + ":/"
    packet += ztime + lat + "/" + lon
    #packet += "102345z" + lat + "/" + "09532.31W"
    packet += "O000/000/A=" + alt + comments

    logging.info(f" packet = {packet}")

    # send packet through parser for validation
    try:
        x = aprslib.parse(packet)
    except (aprslib.ParseError, aprslib.UnknownFormat) as err:
        logging.critical(f" ***** Parsing Error - {err}" )
        return -1
    except:
        logging.critical(f" ***** Unknown Parsing Error - {traceback.format_exc()}" )
        return -1


    AIS = aprslib.IS(uCallsign, passCode, port=14580)
    try:
        AIS.connect()
    except (aprslib.ConnectionError, aprslib.ConnectionDrop) as errc:
        logging.critical(f" ***** Parsing Error - {errc} {errc.message}" )
        return -1
    except aprslib.LoginError as errl:
        logging.critical(f" ***** Login Error - {errl} {errl.message}" )
        return -1
    except:
        logging.exception(f" ***** Unknown Connect Error - {traceback.format_exc()}" )
        return -1

    response = AIS.sendall(packet)
    #aprslib.ConnectionError !!!!!!
    #response = ""
    #if response != "None":
        #logging.critical(f" ***** Sendall Error - {response}" )
    
    return 0

"""
if __name__ == "__main__":
    jUploadData = {
	'software_name': 'k5map-python', 
	'software_version': '0.1', 
	'uploader_callsign': 'W5MOM', 
	'time_received': '2023-07-31T03:26:00.000Z', 
	'payload_callsign': 'K5WH-117', 
	'datetime': '2023-07-31T03:26:10.000Z', 
	'lat': 30.646, 
	'lon': 131.708, 
	'alt': 17100, 
	'grid': 'PM50up', 
	'comment': 'BVARC Brazos Valley ARC Field Day, STX BLT 1163'
	} 
    BalloonCallsign = "K5WH/B"
    putAprsIS(BalloonCallsign, jUploadData)
"""