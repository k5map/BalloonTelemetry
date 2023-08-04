import logging
#import urllib2
import urllib.request, urllib.error
#from StringIO import StringIO
import gzip
import json
import pprint

from miscFunctions import *

# SondeHub datetime format = "2023-07-21T22:29:15.000000Z"
#   
# ???

url = 'https://api.v2.sondehub.org/amateur/telemetry/K5WH-117?format=json'     # will only return records as far back as 24 hours
req = urllib.request.Request(url)
req.add_header('Accept-Encoding', 'gzip')
with urllib.request.urlopen(req) as response:
#    content = response.read()
    content = gzip.decompress(response.read())
decomp_req = content.splitlines()
for line in decomp_req:
    #print(line.decode('utf-8'))
    req_complete = line.decode('utf-8')

print(req_complete)
print('---------------')
JSON = json.loads(req_complete)
print(JSON)
print('---------------')
print(JSON[0])
print('---------------')

print(JSON[0]['payload_callsign'])
for x in JSON:
    print(x['datetime'])
    y = UTCtoEpoch(x['datetime'], '%Y-%m-%dT%H:%M:%S.%fZ')
    print(y)
    z = EpochtoUTC(y, '%Y-%m-%d %H:%M:%S')
    print(z)
    print(" ")

#print(JSON[0]['payload_callsign'])

# x in y to search JSON
# need to keep last position record received

# https://linuxhint.com/search_json_python/   example 5