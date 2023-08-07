
# Balloon Telemetry

A Python script to process Amateur Radio balloon data from [WSPR Live](https://wspr.live/)  and upload it to multiple sites where it can be tracked on [SondeHub](https://amateur.sondehub.org/) and [APRS.fi](https://aprs.fi/) web sites.

This script is currently under development and is not ready for use.  The initial release is expected in the next two weeks.

## Balloon Trackers Supported

* Zachtek
* AB5SS pico - currently under development
* QRP-Labs LightAPRS-W - future release
* QRP-Labs U4B - future release

## Features

* Utilizes a config file to provide details on each balloon
* Designed to have mulitple instances running using a single CFG config file
* Downloads transmitted position data from [WSPR Live](https://wspr.live/) 
* Matches position data
* Depending on which tracker is selected, will decode data within position data to obtain telemetry data
* Uploads processed data to different websites based on INI config file
* If set in CFG config file, will also output data to flat file

## Contribute

Don't hesitate to report any issues, or suggest improvements. Just visit the [issues page](https://github.com/k5map/BalloonTelemetry/issues).
If you wish to assist with development, please contact me prior to making a Pull request.

## Installation

Requirements: Python v3.x

    $ git clone https://github.com/k5map/BalloonTelemetry 
    $ pip install urllib3
    $ pip install requests
    $ pip install maidenhead

## Planned Enhancements

* Modify logging envirnment to use logging.conf file to allow user to set logging levels & output
* Calculate speed of Zachtec tracker 

## Original developer

Author: Mike Pate - K5MAP, [email](mailto:k5map@arrl.net?subject=[GitHub]BalloonTracker)