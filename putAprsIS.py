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
#       K5WH-117>APRS,TCPIP*,qAS,W5MOM:/302315z3038.46N/13142.29EO000/000/A=056105 17100 K5WH-117 PM50up (bCallsign) BVARC Brazos Valley ARC Field Day, STX BLT 1163
#       lat/lon - decimal to radian     https://github.com/ampledata/aprs/blob/master/aprs/decimaldegrees.py
#       time = 121234z  (12th day at 1234 military time)
#==============================================================================================================#

import logging
import traceback
import aprslib
import datetime
#import pprint
import math
from miscFunctions import *


def putAprsIS(BalloonCallsign, jUploadData):
    logging.info("#" + ("-"*130))
    logging.info(" Function putAprsIS start" )

    Callsign = jUploadData['payload_callsign']
    uCallsign = jUploadData['uploader_callsign']
    passCode = getPassCode(uCallsign)

    # build raw_timestamp 
    t1 = datetime.datetime.strptime(jUploadData['time_received'], "%Y-%m-%dT%H:%M:%S.%fZ")
    ztime = t1.strftime("%d%H%Mz")


    # lat / lon
    lat = deg_to_dms(jUploadData['lat'], 'lat')
    lon = deg_to_dms(jUploadData['lon'], 'lon')

    # calc atitude (feet)
    alt_ft = round(jUploadData['alt'] * 3.281)
    alt = f'{alt_ft:06}'

    # build comment field
    comments = f" {jUploadData['alt']} {Callsign} {jUploadData['grid']} {BalloonCallsign} {jUploadData['comment']}"

    # build packet string
    packet = Callsign + ">APRS,TCPIP*,qAS," + uCallsign + ":/"
    packet += ztime + lat + "/" + lon
    packet += "O000/000/A=" + alt + comments

    logging.warning(f" packet = {packet}")        #!!!!!!!! change to debug

    try:
        x = aprslib.parse(packet)
    except (aprslib.ParseError, aprslib.UnknownFormat) as err:
        logging.critical(f" ***** Parsing Error - {err}" )
        return -1
    except:
        logging.critical(f" ***** Unknown Parsing Error - {traceback.format_exc()}" )
        return -1

    logging.warning(f" Parse response: \n {x}" )      #!!!!!!!!!!!  change to debug

    AIS = aprslib.IS(uCallsign, passCode, port=14580)
    try:
        AIS.connect()
    except (aprslib.ConnectionError, aprslib.ConnectionDrop) as errc:
        logging.critical(f" ***** Parsing Error - {errc}" )
        return -1
    except aprslib.LoginError as errl:
        logging.critical(f" ***** Login Error - {errl}" )
        return -1
    except:
        logging.exception(f" ***** Unknown Connect Error - {traceback.format_exc()}" )
        return -1

    #response = AIS.sendall(packet)
    #aprslib.ConnectionError !!!!!!
    response = ""
    if response != "None":
        logging.critical(f" ***** Sendall Error - {response}" )

    
    return 0


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