from lib import url
import time
try: import json
except ImportError: import simplejson as json

def isOldEntry(endTime, lowerBound):
    endTime    = time.mktime(time.strptime(endTime, "%Y-%m-%dT%H:%M:%SZ"))
    lowerBound = time.mktime(time.strptime(lowerBound, "%Y-%m-%dT%H:%M:%SZ"))
    return endTime < lowerBound

def getDowntimes(downtimeMetricURL, lowerBound = None):
    # get downtimes from dashboard and parse json
    dashboardDT  = json.loads(url.read(downtimeMetricURL))

    # downtime events to be inserted
    # structure: {1 : [entry1, entry2], 2 : [entry3, entry4, ..] ..}
    downtimeEvents = {}

    for i in dashboardDT['csvdata']:
        color = i['COLORNAME']
        site  = i['VOName']
        tier  = int(site[1])
        stat  = i['Status']

        # slot start and end times
        start = i['Time']    + 'Z'
        end   = i['EndTime'] + 'Z'

        # skip the entry if it is not downtime
        if color == 'green': continue
        # create google calendar entry summary
        summary = "%s %s [%s to %s]" % (site, stat,
                                        start.replace('T', ' ').replace('Z', ''),
                                        end.replace('T', ' ').replace('Z', ''))
        # if service partially down, put the hash mark before the event summary
        # (please, go to the dashboard::siteStatusBoard metric number 121 and
        # see the metric details to understand better)
        if color == 'yellow':
            summary = '# ' + summary

        downtimeEvent = {'summary' : summary,
            'start': {'dateTime': start, 'timeZone' : 'UTC'},
            'end' :  {'dateTime': end  , 'timeZone' : 'UTC'} }

        # check if the downtime entry is in the lower bound
        if lowerBound and isOldEntry(end, lowerBound):
            print '# skip: %s' % summary
            continue

        if not tier in downtimeEvents:
            downtimeEvents[tier] = []

        if not downtimeEvent in downtimeEvents[tier]:
            downtimeEvents[tier].append(downtimeEvent)

    return downtimeEvents
