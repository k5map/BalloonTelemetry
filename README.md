
# Balloon Telemetry
example:  https://github.com/projecthorus/sondehub-amateur-tracker

A Python script to process Amateur Radio balloon data from [WSPR Live](https://wspr.live/)  and upload it to multiple sites where it can be tracked on [SondeHub](https://amateur.sondehub.org/) and [APRS.fi](https://aprs.fi/) web sites.

Currently this script is under development and is not consider ready for use.  The initial release is expected in the next two weeks.

A webapp for tracking radiosondes. Works an desktop and mobile devices.
The SondeHub Amateur tracker is a continuation of [tracker.habhub.org](https://tracker.habhub.org/).

## Balloon Trackers Supported

* Zachtek
* AB5SS pico - currently under development
* QRP-Labs pico - future release
* U4B pico - future release

## Features

* Utilizes a INI config file to provide details on each balloon
* Designed to have mulitple instances running using a single INI config file
* Downloads transmitted position data from [WSPR Live](https://wspr.live/) 
* Matches position data
* Depending on which tracker is selected, will decode data within position data to obtain telemetry data
* Will upload processed data to different websites based on INI config file
* If set in INI config file, will also output data to flat file

## Contribute

Don't hesitate to report any issues, or suggest improvements. Just visit the [issues page](https://github.com/k5map/sondehub-amateur-tracker/issues).
If you wish to assist with development, please contact me prior to making a Pull request.

## Installation

Requirements: Java

    $ git clone https://github.com/projecthorus/sondehub-amateur-tracker.git
    $ pip install urllib3
    $ pip install requests
    $ pip install maidenhead

## Original developer

Author: Mike Pate - K5MAP