#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# getZachtec                                                                                                   #
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
#import time
#import datetime
from socket import *
from typing import Dict, List
import pprint

from miscFunctions import *
from constants import __version__, SOFTWARE_NAME

#--------------------------------------------------------------------------------------------------------------#

def matchZachtekRecords(aDateTime: List, index: int) -> int:
    # determine if 2nd record avilable to process
    
    # add 2 minutes to found record datetime0
    sDateTime2 = adjDateTime(aDateTime[index]['time'])

    record_found = False
    for x in range(index+1, len(aDateTime)):
        if aDateTime[x]['time'] == sDateTime2:
            # found 2nd record to process
            record_found = True
            break
    if record_found:
        return x
    else:
        return -1

#--------------------------------------------------------------------------------------------------------------#

def getZachtek(wCallsign: str, uCallsign: str, bCallsign: str, timeslot: str, last_date: str, strComment: str):
    """
    Takes a CALLSIGN and gets WSPR spots for that callsign from WSPR Live
    """
    logging.info("#" + ("-"*130))
    logging.info(" Function getZachtek start" )

    query = "SELECT * FROM rx WHERE tx_sign='" + wCallsign + "' AND time > '" + last_date + "' ORDER BY time"

    logging.info(" SQL query = " + query )

    url = "https://db1.wspr.live/?query=" + urllib.parse.quote_plus(query + " FORMAT JSON")

    # download contents from wspr.live
    try:
        contents = urllib.request.urlopen(url).read()
    except urllib.error.URLError as erru:
        logging.critical(f" URL error - {erru.reason}" )
        return -1, None
    except urllib.error.HTTPError as errh:
        logging.critical(f" HTTP error - {errh}" )
        return -1, None
    except socket.timeout as errt:
        logging.critical(f" Connection timeout - {errt}" )
        return -1, None
    except:
        logging.critical(f" Unexpected error calling URL - {traceback.format_exc()}" )
        return -1, None

    # check on how many rows returned
    jWsprData = json.loads(contents.decode("UTF-8"))["data"]
    record_count = len(jWsprData)
    logging.info(f" WSPR Live records downloaded = {record_count}" )
    if record_count < 2:
        logging.warning(" Exit function, insufficient WSPR records to process" )
        return 0, None, None

    #pprint.pp(jWsprData)
    aDateTime = []
    aMatch = []
    # build array of 'time' from WSPR data (i.e., 2023-07-23 06:36:00)
    for i in range(len(jWsprData)):
        try:
            aDateTime.index(jWsprData[i]['time'])
        except ValueError:
            rCode = matchZachtekRecords(jWsprData, i)
            if rCode != -1:
                aDateTime.append(jWsprData[i]['time'])
                aMatch.append(i)
                aMatch.append(rCode)
                logging.info(f" Found 1st record (index={i}) to process = {jWsprData[i]['time']}")
                logging.info(f" Found 2nd record (index={rCode}) to process = {jWsprData[rCode]['time']}")

    logging.info(f" Number of unique records identified: {len(aMatch)}")
    logging.debug(f" aMatch = {aMatch}")
    logging.debug(f" wDateTime = {aDateTime}")

    if len(aMatch) < 2:
        logging.warning(" No new WSPR records matched to process")
        return 0, None, None
    logging.info(f" New lDateTime = {jWsprData[aMatch[len(aMatch)-1]]['time']}")


    # found at least 1 set matched, assemble json for upload
    jUploadData = []
    for i in range(0, len(aMatch), 2):
        x = aMatch[i]       # Index to 1st record
        j = i + 1
        y = aMatch[j]       # Index to 2nd record
        # calc lat/lon from grid
        pos = GridtoLatLon(jWsprData[y]['tx_loc'])              # use Grid from 2nd packet
        lat = round(pos[0],3)
        lon = round(pos[1],3)

        # calc altitude from power
        # reference https://github.com/HarrydeBug/WSPR-transmitters/blob/master/Standard%20Firmware/Release/Hardware_Version_2_ESP8285/WSPR-TX2.05/WSPR-TX2.05.ino line 1430
        altitude = (int(jWsprData[x]['power']) + int(jWsprData[y]['power'])) * 300
        logging.debug(f" alt1/power = {jWsprData[x]['power']}, alt2/power = {jWsprData[y]['power']}, altitude = {altitude}m")

        ##logging.info(" Altitude: meters = " + str(altitude) + ", feet = " + str(round(altitude*3.28084)))
        logging.info(f" DateTime: {jWsprData[y]['time']}, Grid: {jWsprData[y]['tx_loc']}, Lat: {lat}, Lon: {lon}, Alt: {altitude}m {round(altitude*3.28084)}ft, x-y {x} {y}")

        # reformat time from WSPR format to Zulu
        datetime1 = reformatDateTime(jWsprData[y]['time'], 0)
        datetime2 = reformatDateTime(jWsprData[y]['time'], 10)

        # assemble json for upload to SondeHub
        JSON = {"software_name" : SOFTWARE_NAME, "software_version" : __version__, "uploader_callsign" : uCallsign, "time_received" : datetime1,
            "payload_callsign" : bCallsign, "datetime" : datetime2, "lat" : lat, "lon" : lon, "alt" : altitude, "grid" : jWsprData[y]['tx_loc'], "comment" : strComment}
        jUploadData.append(JSON)

    logging.debug(f" jUploadData records = {len(jUploadData)}")
    print("----------------------------------------")
    #pprint.pp(jUploadData[i], indent=2)
    l = len(aMatch)
    pprint.pp(jWsprData[aMatch[l-2]], indent=2)
    pprint.pp(jWsprData[aMatch[l-1]], indent=2)

    return 1, jUploadData, jWsprData[y]['time']
