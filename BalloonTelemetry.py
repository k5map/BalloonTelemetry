#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# aprsWsprBridge.py - simple python script to collect WSPR spots and upload a position to APRS                 #
#                                                                                                              #
# Copyright (C) 2023 Mike Pate - K5MAP                                                                         #
#                                                                                                              #
#==============================================================================================================#
#
# if not already installled, use pip to install the following
#
#    pip install aprslib
#    pip install pprint
#
#==============================================================================================================#
#
#  2023 07-20 - 
#
#==============================================================================================================#
#  Resources
#       logging - https://www.youtube.com/watch?v=KSQ4KxCtsf8 
#       aprslib - https://aprs-python.readthedocs.io/en/stable/
#       SondeHub-APRS gateway - https://github.com/projecthorus/sondehub-aprs-gateway 
#==============================================================================================================#

# Trackers
# Z = Zachtek keeps the callsign on both
# A = AB5SS robs the callsign on the 2nd packet and requires decoding
# Q = QRP-Labs robs the callsign on the 2nd packet and requires decoding
# U = U4B robs the callsign on the 2nd packet and requires decoding

import sys
import logging
import string
import datetime
import time
import calendar
import json
import pprint

from BalloonCfg import *
from getZachtek import *
from getAB5SS import *
from putSondeHub import *
from putAprsIS import *
from miscFunctions import *
from constants import __version__


#------------------------ starts here -----------------------------#
BalloonCfg = getBalloonCfg()
logFile = BalloonCfg['ballooncallsign'] + ".log"
print(f"*** {BalloonCfg['ballooncallsign']} CFG ***")
pprint.pp(BalloonCfg)

#------------------------ configure logging -----------------------------#
logging.basicConfig(filename = logFile,
                    level = logging.DEBUG,
                    format = '%(asctime)s - %(levelname)-8s :%(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    filemode = 'w')
logging.info(f" Program version {__version__}")
logging.info("#" + ("-"*130))

if sys.version_info[0] > 3 :
    logging.critical(' Tested on only Python ver 3.x')
    raise Exception( 'Tested on only Python ver 3.x' )
else :
    logging.info(' Cleared to continue')

logging.info(f" Loaded these values for balloon {BalloonCfg['ballooncallsign']}" )
for k, v in BalloonCfg.items():
    # print (k, v)
    logging.info(f" \t- {k} = {v}" )

strUploadCallSign = BalloonCfg['uploadcallsign']
strWsprCallSign = BalloonCfg['wsprcallsign']
strBalloonCallSign = BalloonCfg['ballooncallsign']
timeslot = int(BalloonCfg['timeslot'])
tracker = BalloonCfg['tracker']
strComment = BalloonCfg['comment']
UploadSite = BalloonCfg['uploadsite']
TelemetryFile = BalloonCfg['telemetryfile']
lDateTime = BalloonCfg['ldatetime']

#------------------- verify user var ------------------------------#
if VerifyCallsign(strUploadCallSign) != True :
    logging.error(f" Callsign {strUploadCallSign} is NOT valid" )
    sys.exit( "Invalid callsign specified" )
else :
    logging.info(f" Callsign {strUploadCallSign} is valid" )

if VerifyCallsign(strWsprCallSign) != True :
    logging.error(f" Callsign {strWsprCallSign} is NOT valid" )
    sys.exit( "Invalid callsign specified" )
else :
    logging.info(f" Callsign {strWsprCallSign} is valid" )

if VerifyCallsign(strBalloonCallSign) != True :
    logging.error(f" Callsign {strBalloonCallSign} is NOT valid" )
    sys.exit(f" Invalid callsign specified" )
else :
    logging.info(f" Callsign {strBalloonCallSign} is valid" )

strLastTime = lDateTime

#------------ determine which tracker selected -----------------------------#
match tracker:
    case "Z":
        #  Zachtek tracker selected
        logging.info(f" Tracker selected = {tracker} (Zacktek)" )
        rCode, jUploadData, lastDateTime = getZachtek(strWsprCallSign, strUploadCallSign, strBalloonCallSign, timeslot, strLastTime, strComment )

        if rCode == -1 :     # some sort of exception occured, check log
            sys.exit( 1 )

    case "A":
        #  AB5SS tracker selected
        logging.info(f" Tracker selected = {tracker} (AB5SS pico)" )
        rCode, jUploadData, lastDateTime = getAB5SS(BalloonCfg, strLastTime)
        if rCode == -1 :     # some sort of exception occured, check log
            sys.exit( 1 )

    case "Q":
        #  QRP-Labs tracker selected
        logging.info(f" Tracker selected = {tracker} (QRP-Labs)" )
        # call function
        rCode = 0       #!!!!!!!!!!!!!!!!!!!!!!!!!!
        if rCode == -1 :     # some sort of exception occured, check log
            sys.exit( 1 )

    case "U":
        #  U4B tracker selected
        logging.info(f" Tracker selected = {tracker} (U4B)" )
        # call function
        rCode = 0       #!!!!!!!!!!!!!!!!!!!!!!!!!!
        if rCode == -1 :     # some sort of exception occured, check log
            sys.exit( 1 )

    case _:
        #  Invalid tracker selected
        logging.critical(f" Tracker selected = {tracker}, *** not valid ***" )
        sys.exit( 1 )


#------------ uplaod results, if data found -----------------------------#
if rCode == 1:
    # check uploadsite var to determine which site to upload data
    match UploadSite:
        case "S":
            # SondeHub
            result = putSondeHub(jUploadData)
            if result == -1 :     # some sort of exception occured, check log
                sys.exit( 1 )

        case "A":
            # APRS-IS
            result = putAprsIS(strWsprCallSign, jUploadData)
            if result == -1 :     # some sort of exception occured, check log
                sys.exit( 1 )

        case "T":
            # Do not upload - this option for testing
            logging.info(f" NOTE: No upload attempted, CFG indicates testing only" )
            rCode = 0

        case _:
            #  Invalid Upload Site selected
            logging.critical(f" *** Invalid Upload Site = {UploadSite}" )
            sys.exit( 1 )


#------------ save last update date & time -----------------------------#
if rCode == 1:
    logging.info(" ")
    logging.info(f" Update lDateTime in CFG with = {lastDateTime}")
    putBalloonCfg(strBalloonCallSign, lastDateTime)


#----------------------- last log entry -----------------------------#
logging.info(" Application Ending " + ("*"*111))
sys.exit( 0 )