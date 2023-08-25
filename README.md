
# Balloon Telemetry

A Python script to process Amateur Radio balloon data from [WSPR Live](https://wspr.live/)  and upload it to multiple sites where it can be tracked on [SondeHub](https://amateur.sondehub.org/) and [APRS.fi](https://aprs.fi/) web sites.


## Balloon Trackers Supported

* Zachtek
* AB5SS pico
* QRP-Labs LightAPRS-W - in development 
* QRP-Labs U4B/Tranquito

## Features

* Utilizes a config file to provide details on each balloon
* Designed to have mulitple instances running using a single CFG config file
* Downloads transmitted position data from [WSPR Live](https://wspr.live/) 
* Matches 1st and 2nd position data records
* Depending on which tracker is selected, will decode data within position data to obtain telemetry data
* Uploads processed data to different websites based on CFG config file
* If set in CFG config file, will also output data to flat file
  - Telemetry data saved:  callsign, time, channel, grid, speed, altitude, temp, sun azimuth, sun elevation

## Contribute

Don't hesitate to report any issues, or suggest improvements; just visit the [issues page](https://github.com/k5map/BalloonTelemetry/issues).
If you wish to assist with development, please contact me prior to making a Pull request.

## Installation

Requirements: Python v3.x

    $ git clone https://github.com/k5map/BalloonTelemetry 
    $ pip install urllib3
    $ pip install requests
    $ pip install maidenhead
    $ pip install configupdater

## Execution

    $ python BalloonTelemetry.py callsign-999   [balloon callsign and SSID to be shown on APRS.fi or SondeHub ]


## Testing

Within the CFG file, set the value of uploadsite = T.  This will process all of the data, prepare it for uploading but not acutally
upload any data. This way you get a full run and can view the log file for any errors.

## Planned Enhancements

* Modify logging envirnment to use logging.conf file to allow user to set logging levels & output
* Calculate speed for Zachtec tracker 

## Original developer

Author: Mike Pate ([email](mailto:k5map@arrl.net?subject=[GitHub]BalloonTracker)) - K5MAP