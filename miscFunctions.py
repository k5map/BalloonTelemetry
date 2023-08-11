#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# aprsUtilies - collction of functions used by wsprAPRSBridge.py                                               #
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
#    pip install aprslib3
#    pip install maidenhead
#
#==============================================================================================================#
#
#  Convert QTH locator (or Maidenhead) to Lat/Lon:  https://www.giangrandi.org/electronics/radio/qthloccalc.shtml 
#  Formula to convert grid to lat/lon:  https://www.m0nwk.co.uk/how-to-convert-maidenhead-locator-to-latitude-and-longitude/
#  Solar calc:  https://pvlib-python.readthedocs.io/en/stable/_modules/pvlib/solarposition.html 

import aprslib
import calendar
import time
import datetime
import math
import re                        #regex
import maidenhead as mh


#==============================================================================================================#
#                                                                                                              #
# getPassCode(callsign)                                                                                        #
# - returns 4 digit number used by APRS-IS API                                                                 #
#                                                                                                              #
#==============================================================================================================#
def getPassCode(strCallsign):
    """
    Takes a CALLSIGN and returns passcode for APRS-IS
    """
    PassCode = aprslib.passcode(strCallsign)
    return PassCode


#==============================================================================================================#
#                                                                                                              #
# adjDateTime()                                                                                                #
# - returns a datetime string where the time has been increased by 2 minutes                                   #
#                                                                                                              #
#==============================================================================================================#
def adjDateTime(sDateTime):
    """
    Takes a datetime string (YYYY-MM-DD HH:MM:SS) and adds 2 minutes
    """
    given_time = datetime.datetime.strptime(sDateTime, "%Y-%m-%d %H:%M:%S")
    future = given_time + datetime.timedelta(minutes=2)
    adjDT = future.strftime("%Y-%m-%d %H:%M:%S")
    return adjDT


#==============================================================================================================#
#                                                                                                              #
# deg_to_dms                                                                                                   #
# - converts decimal degrees (99.9999) to degree, mintue, seconds                                              #
# - returns (DDDMM.SSc where c = N, S, W, E                                                                    #
#                                                                                                              #
#==============================================================================================================#
def deg_to_dms(deg, type='lat'):
    decimals, number = math.modf(deg)
    d = int(number)
    m = int(decimals * 60)
    s = (deg - d - m / 60) * 3600.00
    compass = {
        'lat': ('N','S'),
        'lon': ('E','W')
    }
    compass_str = compass[type][0 if d >= 0 else 1]
    dStr = f"{abs(d):02}" if type == 'lat' else f"{abs(d):03}"
    return f'{dStr}{abs(m):02}.{abs(s):02.0f}{compass_str}'
    #return f'{abs(d):05}{abs(m):02}.{abs(s):02.0f}{compass_str}'


#==============================================================================================================#
#                                                                                                              #
# GridtoLatLon                                                                                                 #
# - converts QTH grid (Maidenhead) to Lat/Lon                                                                  #
# - returns (30.020833333333332, -95.54166666666666) - each are float vars                                     #
#                                                                                                              #
#==============================================================================================================#
def GridtoLatLon(grid):
    # split each char of grid
    # Ascii = ord ('E') = 69
    return mh.to_location(grid, center=True)


#==============================================================================================================#
#                                                                                                              #
# FreqToBand                                                                                                   #
# - converts TX frequency to band                                                                              #
# - returns band as integer                                                                                    #
#                                                                                                              #
#==============================================================================================================#
def FreqToBand(freq):
    # 14097093 example from WSPR frequency field
    # 10, 12, 15, 17, 20, 40, 80
    f = freq / 1000000
    if f < 4.0:
        band = 80
    elif f < 7.2:
        band = 40
    elif f < 10.2:
        band = 30
    elif f < 14.5:
        band = 20
    elif f < 18.2:
        band = 17
    elif f < 21.5:
        band = 15
    elif f < 24.99:
        band = 12
    elif f < 29.8:
        band = 10
    else:
        band = 0
    return band


#==============================================================================================================#
#                                                                                                              #
# UTCtoEpoch(dateTime)                                                                                         #
# - converts datetime string '2023-07-20 06:04:00' to Epoch time integer                                       #
# - returns Epoch as integer                                                                                   #
#                                                                                                              #
#==============================================================================================================#
def UTCtoEpoch(strDateTime, fCode):
    #intEpoch = calendar.timegm(time.strptime(strDateTime, '%Y-%m-%d %H:%M:%S'))
    intEpoch = calendar.timegm(time.strptime(strDateTime, fCode))
    return intEpoch


#==============================================================================================================#
#                                                                                                              #
# reformatDateTime(dateTime1, offset)                                                                          #
# - converts datetime string 'YYYY-MM-DD HH:MM:SS' to Zulu 'YYYY-MM-DDTHH:MM:SSZ                               #
#                                                                                                              #
#==============================================================================================================#
def reformatDateTime(strDateTime, offset):
    t1 = datetime.datetime.strptime(strDateTime, "%Y-%m-%d %H:%M:%S")
    if offset > 0:
        t2 = t1 + datetime.timedelta(seconds=offset)
    else:
        t2 = t1
    #datetime1 = t1.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    #datetime2 = t2.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return t2.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"



#==============================================================================================================#
#                                                                                                              #
# EpochtoUTC(epoch)                                                                                            #
# - converts Epoch integer to datetime string '2023-07-20 06:04:00'                                            #
# - returns datetime as string                                                                                 #
#                                                                                                              #
#==============================================================================================================#
def EpochtoUTC(intEpoch, fcode):
    # strDateTime = datetime.datetime.fromtimestamp(intEpoch).strftime('%Y-%m-%d %H:%M:%S')
    strDateTime = datetime.datetime.utcfromtimestamp(intEpoch).strftime(fcode)
    return strDateTime


#==============================================================================================================#
#                                                                                                              #
# VerifyCallsign(callsign)                                                                                     #
# - verifies string is a valid callsign                                                                        #
# - returns boolean                                                                                            #
#                                                                                                              #
#==============================================================================================================#
def VerifyCallsign(strCallSign):
    callsign = strCallSign
    if (i := strCallSign.find('-')) > 0:
        callsign = strCallSign[0:i]
    if (i := strCallSign.find('/')) > 0:
        callsign = strCallSign[0:i]

    if (re.search('^(?:(?:[1-9][A-Z][A-Z]?)|(?:[A-Z][2-9A-Z]?))[0-9][A-Z]{1,3}$', callsign) ) :
        return True
    else:
        return False
    


if __name__ == "__main__":
    #logging.info("Current Log Level : {}\n".format(logging.getLevel()))
    sDateTime = '2023-08-02 23:58:00'
    x = adjDateTime(sDateTime)
    print(f" sDateTime = {sDateTime}, adjDateTime = {x}")