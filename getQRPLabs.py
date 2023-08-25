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

def matchQRPRecords(jWSPRRec1: List, jWSPRRec2: List) -> List:
    # determine if 2nd record avilable to process
    logging.info(f" Starting record matching process")

    print(f"jWSPRRec1 len = {len(jWSPRRec1)}")
    print(f"jWSPRRec2 len = {len(jWSPRRec2)}")

    aDateTime = []
    aMatch = []
    for i in range(0, len(jWSPRRec1)):
        try:
            aDateTime.index(jWSPRRec1[i]['time'])
        except ValueError:
            aDateTime.append(jWSPRRec1[i]['time'])
            sDateTime = adjDateTime(jWSPRRec1[i]['time'])           # find 2nd record time based on 1st record
            match = False
            for j, element in enumerate(jWSPRRec2):
            #for j in range(len(jWSPRRec2)):
                if element['time'] == sDateTime:
                    match = True
                    break
            # process both records
            if match == True:
                aMatch.append(jWSPRRec1[i])
                aMatch.append(jWSPRRec2[j])
                logging.debug(f" Found 1st record to process = {jWSPRRec1[i]['tx_sign']}, {jWSPRRec1[i]['time']}, {jWSPRRec1[i]['tx_loc']}, {jWSPRRec1[i]['band']}")
                logging.debug(f" Found 2nd record to process = {jWSPRRec2[j]['tx_sign']}, {jWSPRRec2[j]['time']}, {jWSPRRec2[j]['tx_loc']}, {jWSPRRec2[j]['band']}")
            else:
                logging.debug(f" Found 1st record to process but no match = {jWSPRRec1[i]['tx_sign']}, {jWSPRRec1[i]['time']}, {jWSPRRec1[i]['tx_loc']}, {jWSPRRec1[i]['band']}")
    return aMatch

#--------------------------------------------------------------------------------------------------------------#

def decodeQRP(JSON1: Dict, JSON2: Dict) -> Dict:
    pow2dec = {0:0,3:1,7:2,10:3,13:4,17:5,20:6,23:7,27:8,30:9,33:10,37:11,40:12,43:13,47:14,50:15,53:16,57:17,60:18}

    spot_pos_time = JSON1['time']
    spot_pos_call = JSON1['tx_sign']
    spot_pos_loc = JSON1['tx_loc']
    #spot_pos_power = 17
    spot_tele_call = JSON2['tx_sign']
    spot_tele_loc = JSON2['tx_loc']
    spot_tele_power = int(JSON2['power'])
    
    # Convert call to numbers
    c1 = spot_tele_call[1]
    # print("C1=",c1)
    if c1.isalpha():
        c1 = ord(c1) - 55
    else:
        c1 = ord(c1) - 48

    c2 = ord(spot_tele_call[3]) - 65
    c3 = ord(spot_tele_call[4]) - 65
    c4 = ord(spot_tele_call[5]) - 65

    # Convert locator to numbers
    l1 = ord(spot_tele_loc[0]) - 65
    l2 = ord(spot_tele_loc[1]) - 65
    l3 = ord(spot_tele_loc[2]) - 48
    l4 = ord(spot_tele_loc[3]) - 48

    #
    # Convert power
    #
    p = pow2dec[spot_tele_power]
    sum1 = c1 * 26 * 26 * 26
    sum2 = c2 * 26 * 26
    sum3 = c3 * 26
    sum4 = c4
    sum1_tot = sum1 + sum2 + sum3 + sum4

    sum1 = l1 * 18 * 10 * 10 * 19
    sum2 = l2 * 10 * 10 * 19
    sum3 = l3 * 10 * 19
    sum4 = l4 * 19
    sum2_tot = sum1 + sum2 + sum3 + sum4 + p
    # print("sum_tot1/2:", sum1_tot,sum2_tot)

    # 24*1068
    lsub1 = int(sum1_tot / 25632)
    lsub2_tmp = sum1_tot - lsub1 * 25632
    lsub2 = int(lsub2_tmp / 1068)
    # print("lsub1/2",lsub1,lsub2)
    alt = (lsub2_tmp - lsub2 * 1068) * 20

    # Handle bogus altitudes
    if  alt > 14000:
        # print("Bogus packet. Too high altitude!! locking to 9999")
        alt = 9999
        
    if alt == 2760:
        # print("Bogus packet. 2760 m  locking to 9998")
        alt = 9998

    if alt == 0:
        # print("Zero alt detected. Locking to 10000")
        alt = 10000

    # Sublocator
    lsub1 = lsub1 + 65
    lsub2 = lsub2 + 65
    subloc = (chr(lsub1) + chr(lsub2)).lower()

    # Temperature
    # 40*42*2*2
    temp_1 = int(sum2_tot / 6720)
    temp_2 = temp_1 * 2 + 457
    temp_3 = temp_2 * 5 / 1024
    temp = (temp_2 * 500 / 1024) - 273
    # print("Temp: %5.2f %5.2f %5.2f %5.2f" % (temp_1, temp_2, temp_3, temp))
    
    #
    # Battery
    #
    # =I7-J7*(40*42*2*2)
    batt_1 = int(sum2_tot - temp_1 * 6720)
    batt_2 = int(batt_1 / 168)
    batt_3 = batt_2 * 10 + 614
    # 5*M8/1024
    batt = batt_3 * 5 / 1024

    #
    # Speed / GPS / Sats
    #
    # =I7-J7*(40*42*2*2)
    # =INT(L7/(42*2*2))
    t1 = sum2_tot - temp_1 * 6720
    t2 = int(t1 / 168)
    t3 = t1 - t2 * 168
    t4 = int(t3 / 4)
    speed = t4 * 2
    r7 = t3 - t4 * 4
    gps = int(r7 / 2)
    sats = r7 % 2
    # print("T1-4,R7:",t1, t2, t3, t4, r7)

    #
    # Calc lat/lon from loc+subbloc
    #
    loc = spot_pos_loc + subloc
    lat, lon = GridtoLatLon(loc)
    
    pstr = ("Spot %s Call: %6s Latlon: %10.5f %10.5f Grid: %6s Alt: %5d Temp: %4.1f Batt: %5.2f Speed: %3d GPS: %1d Sats: %1d" %
          ( spot_pos_time, spot_pos_call, lat, lon, loc, alt, temp, batt, speed, gps, sats ))

    telemetry = {'time':spot_pos_time, "call":spot_pos_call, "lat":round(lat,3), "lon":round(lon,3), "grid":loc, "alt": alt,
                 "temp":round(temp,1), "batt":round(batt,2), "speed":speed, "gps":gps, "sats":sats }

    return telemetry

#--------------------------------------------------------------------------------------------------------------#

def getQRPLabs(bCfg: Dict, lastdate: str):
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

    query = "SELECT * FROM rx WHERE tx_sign='" + wCallsign + "' AND time > '" + lastdate + "' ORDER BY time"
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

    # remove any duplicate first packets
    print(40*"-")
    logging.debug(f" starting record count = {len(jWsprData)}")
    jWsprData = deldupWspr(jWsprData)
    logging.debug(f" ending record count after removing duplicates = {len(jWsprData)}")

    # process CFG values to search for 2nd packets
    ch1 = channel[0]
    ch3 = channel[1]
    ts = str(int(timeslot)+2)
    sSign = f"{ch1}_{ch3}%"
    #sTime = '____-__-__ __:_' + ts + '%'
    logging.info(f" Values to use for 2nd packet:  ch1 = {ch1}, ch3 = {ch3}, ts = {ts}, band = {band}, sSign = {sSign}")

    # build query for 2nd packet
    query = "SELECT * FROM rx WHERE tx_sign LIKE '" + sSign + "' AND band=" + band + " AND time > '" + lastdate + "' ORDER BY time"
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

    jWsprData2 = json.loads(contents.decode("UTF-8"))["data"]
    record_count = len(jWsprData2)
    logging.info(f" WSPR Live records downloaded = {record_count}" )
    if record_count < 1:
        logging.warning(" Exit function, insufficient matching WSPR records to process" )
        return 0, None, None
    #pprint.pp(jWsprData2[len(jWsprData2)-1], indent=2)

    # process records downloaded and match
    aMatch = matchQRPRecords(jWsprData, jWsprData2)
    logging.info(f" Number of matched records = {len(aMatch)}" )
    if len(aMatch) < 2:
        # no matches to process
        logging.warning(f" Insuficient number of records to process" )
        return 0, None, None

    #  decode each pair of matches and build upload data list
    logging.info(f" Starting decoding process" )
    jDecodedData = {}
    jUploadData = []
    for i in range(0, len(aMatch), 2):
        jDecodedData[i] = decodeQRP(aMatch[i], aMatch[i+1])

        # reformat time from WSPR format to Zulu
        datetime1 = reformatDateTime(aMatch[i]['time'], 0)
        datetime2 = reformatDateTime(aMatch[i]['time'], 10)

        # add telemetry data
        # build strComment  grid, temp, volt, To:?, Up:?, V?, Sun:?, comment
        strComment = jDecodedData[i]['grid'] + " " + str(jDecodedData[i]['temp']) + "C " + str(jDecodedData[i]['batt']) + "V "
        strComment += "To:?? Up:??m/s V:??Km/h Sun:?? " + bCfg['comment']

        # put data into jUploadData format for uploading
        lat, lon = GridtoLatLon(jDecodedData[i]['grid'])
        JSON = {"software_name":SOFTWARE_NAME, "software_version": __version__, "uploader_callsign": bCfg['uploadcallsign'], "time_received": datetime1,
            "payload_callsign":BalloonCallsign, "datetime":datetime2, "lat":round(lat,3), "lon":round(lon,3), "alt":jDecodedData[i]['alt'], 
            "sats":jDecodedData[i]['sats'], "temp":jDecodedData[i]['temp'], "batt":jDecodedData[i]['batt'], "grid":jDecodedData[i]['grid'], "comment":strComment}
        jUploadData.append(JSON)

    logging.info(f" Decoding completed, record count = {len(jUploadData)}" )
    pprint.pp(jUploadData)

    # if option selected, create data file for John
    if bCfg['telemetryfile'] == 'Y':
        pass

    return  1, jUploadData, aMatch[i]['time']
