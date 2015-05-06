import sys, googleAPI, time
from optparse import OptionParser
from lib import url, fileOps
try: import json
except ImportError: import simplejson as json

#if len(sys.argv) < 4:
#    sys.stderr.write('not enough parameter!\n')
#    sys.exit(1)

parser = OptionParser()
parser.add_option("-k", "--key",    dest="jsonKeyFile", help="Key file for google calendar API",       metavar="FILE")
parser.add_option("-m", "--map",    dest="mapFile",     help="Map file to matche tiers and calendars", metavar="FILE")
parser.add_option("-s", "--source", dest="source",      help="Calendar source url",                    metavar="URL")
(options, args) = parser.parse_args()

if not options.jsonKeyFile or not options.mapFile or not options.source:
    sys.stderr.write('not enough argument. please run python main.py --help.\n')
    sys.exit(1)

credentials  = googleAPI.getCredentials(options.jsonKeyFile)
service      = googleAPI.getService(credentials)

# parse calendar-CMS site tier map file
map          = json.loads(fileOps.read(options.mapFile))

# get downtimes from dashboard and parse json
dashboardDT  = json.loads(url.read(options.source))
downtimes    = []

# get all calendars that are connected with the account
calendarList = service.calendarList().list().execute()

# old calendar events will be stored in this dict.
# The structure is following: {'calendarId' : [events], ...}
oldEvents    = {}

for i in dashboardDT['csvdata']:
    color = i['COLORNAME']
    site  = i['VOName']
    tier  = int(site[1])
    stat  = i['Status']

    # slot start and end times and convert them into unix time
    start = i['Time']
    end   = i['EndTime']
    # skip the entry if it is not downtime
    if color == 'green': continue
    # create google calendar entry summary
    summary = "%s %s [%s to %s]" % (site, stat, start.replace('T', ' '), end.replace('T', ' '))
    # if service partially down, put the hash mark before the event summary
    # (please, go to the dashboard::siteStatusBoard metric number 121 and
    # see the metric details to understand better)
    if color == 'yellow':
        summary = '# ' + summary
    downtimeEvent = {'summary' : summary,
        'start': {'dateTime': start+'Z', 'timeZone' : 'Europe/Zurich'},
        'end' :  {'dateTime': end + 'Z', 'timeZone' : 'Europe/Zurich'} }
    # loop all calendars and check the calendar-tier map
    for i in calendarList['items']:
        calendarName = i['summary']
        calendarId   = i['id']

        # the calendar that is taken by using google api is not in the 
        # calendar-tier map, skip it.
        if not calendarName in map: continue

        # skip site entry from dashboard if .....
        if not tier in map[calendarName]: continue

        # collect evets if they were not collected for this calendar
        # the idea behind collecting old events is to avoid to insert the
        # events already inserted
        if not calendarId in oldEvents:
            oldEvents[calendarId] = []
            pageToken = None
            while True:
                events = service.events().list(calendarId=calendarId, pageToken=pageToken).execute()
                for event in events['items']:
                    oldEvents[calendarId].append(event['summary'])
                pageToken = events.get('nextPageToken')
                if not pageToken:
                    break
        # skip the event if it is already inserted
        if summary in oldEvents[calendarId]:
            print 'Event is already in %s:' % calendarName, summary
            continue

        # insert event
        createdEvent = service.events().insert(calendarId=i['id'], body=downtimeEvent).execute()
        print summary, 'inserted...'
