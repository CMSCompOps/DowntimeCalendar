# aaltunda - ali.mehmet.altundag@cern.ch

import urllib2

def read(url, request = False, header = {}):
    if request: return readCert(url, request)
    request = urllib2.Request(url, headers=header)
    urlObj  = urllib2.urlopen(request)
    data    = urlObj.read()
    return data
