#!/usr/bin/python
#==============================================================================================================#
#                                                                                                              #
# SolarPos -- function to determine the Sun's amimuth & elevation for a specific date, time, location          #
#                                                                                                              #
# Copyright (C) 2023 Mike Pate - K5MAP                                                                         #
#                                                                                                              #
# This program is free software; you can redistribute it and/or modify                                         #
# it under the terms of the GNU General Public License as published by                                         #
# the Free Software Foundation; either version 2 of the License, or                                            #
# (at your option) any later version.                                                                          #
#                                                                                                              #
# Reference https://levelup.gitconnected.com/python-sun-position-for-solar-energy-and-research-7a4ead801777    #
#==============================================================================================================#

import math
from typing import List, Dict, Tuple

def SunPosition(when: Tuple, location: Tuple, refraction: bool) -> Tuple[float, float]:
    """
    Function to determine azimuth and elevation of the Sun

    : param when: datetime, location: tuple(lat, lon), refraction: boolean
    : return: Tuple(azimuth: float, elevation: float)
    """
    # Extract the passed data
    year, month, day, hour, minute, second, timezone = when
    latitude, longitude = location
    
    # Math typing shortcuts
    rad, deg = math.radians, math.degrees
    sin, cos, tan = math.sin, math.cos, math.tan
    asin, atan2 = math.asin, math.atan2
    
    # Convert latitude and longitude to radians
    rlat = rad(latitude)
    rlon = rad(longitude)
    
    # Decimal hour of the day at Greenwich
    greenwichtime = hour - timezone + minute / 60 + second / 3600
    
    # Days from J2000, accurate from 1901 to 2099
    daynum = (
        367 * year
        - 7 * (year + (month + 9) // 12) // 4
        + 275 * month // 9
        + day
        - 730531.5
        + greenwichtime / 24
    )
    
    # Mean longitude of the sun
    mean_long = daynum * 0.01720279239 + 4.894967873
    
    # Mean anomaly of the Sun
    mean_anom = daynum * 0.01720197034 + 6.240040768
    
    # Ecliptic longitude of the sun
    eclip_long = (
        mean_long
        + 0.03342305518 * sin(mean_anom)
        + 0.0003490658504 * sin(2 * mean_anom)
    )
    
    # Obliquity of the ecliptic
    obliquity = 0.4090877234 - 0.000000006981317008 * daynum
    
    # Right ascension of the sun
    rasc = atan2(cos(obliquity) * sin(eclip_long), cos(eclip_long))
    
    # Declination of the sun
    decl = asin(sin(obliquity) * sin(eclip_long))
    
    # Local sidereal time
    sidereal = 4.894961213 + 6.300388099 * daynum + rlon

    # Hour angle of the sun
    hour_ang = sidereal - rasc
    
    # Local elevation of the sun
    elevation = asin(sin(decl) * sin(rlat) + cos(decl) * cos(rlat) * cos(hour_ang))
    
    # Local azimuth of the sun
    azimuth = atan2(
        -cos(decl) * cos(rlat) * sin(hour_ang),
        sin(decl) - sin(rlat) * sin(elevation),
    )
    
    # Convert azimuth and elevation to degrees
    azimuth = into_range(deg(azimuth), 0, 360)
    elevation = into_range(deg(elevation), -180, 180)
    
    # Refraction correction (optional)
    if refraction:
        targ = rad((elevation + (10.3 / (elevation + 5.11))))
        elevation += (1.02 / tan(targ)) / 60
    
    # Return azimuth and elevation in degrees
    return (round(azimuth, 2), round(elevation, 2))

def into_range(x, range_min, range_max):
    shiftedx = x - range_min
    delta = range_max - range_min
    return (((shiftedx % delta) + delta) % delta) + range_min

"""
if __name__ == "__main__":
    # Close Encounters latitude, longitude
    location = (40.602778, -104.741667)
    #location = (37.7749, -122.4194)
    
    # Fourth of July, 2022 at 11:20 am MDT (-6 hours)
    # 2023-08-08 12:00:00
    when = (2022, 7, 4, 11, 20, 0, -6)
    #when = (2023, 8, 8, 12, 0, 0, 0)
    
    # Get the Sun's apparent location in the sky
    azimuth, elevation = SunPos(when, location, True)
    
    # Output the results
    print("\nWhen: ", when)
    print("Where: ", location)
    print("Azimuth: ", azimuth)
    print("Elevation: ", elevation)
    
    # When:  (2022, 7, 4, 11, 20, 0, -6)
    # Where:  (40.602778, -104.741667)
    # Azimuth:  121.38
    # Elevation:  61.91
"""