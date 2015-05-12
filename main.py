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

# downtime events to be inserted
# structure: {1 : [entry1, entry2], 2 : [entry3, entry4, ..] ..}
downtimeEvents = {}

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

    if not tier in downtimeEvents:
        downtimeEvents[tier] = []

    if not downtimeEvent in downtimeEvents[tier]:
        downtimeEvents[tier].append(downtimeEvent)


# get all calendars
calendarList = service.calendarList().list().execute()

# old calendar events will be stored in this dict.
# The structure is following: {'calendarId' : [events], ...}
oldEvents    = {}

# loop all calendars and get old events
for i in calendarList['items']:
    calendarName = i['summary']
    calendarId   = i['id']

    # if the clander is not mapped in the input file, skip it
    if not calendarName in map:
        print 'skip calendar:', calendarName
        continue

    print 'calendar:', calendarName

    # collect old events
    oldEvents[calendarId] = []
    pageToken = None
    while True:
        events = service.events().list(calendarId=calendarId, pageToken=pageToken).execute()
        for event in events['items']:
            oldEvents[calendarId].append(event['summary'])
        pageToken = events.get('nextPageToken')
        if not pageToken:
            break

    # loop for each tier mapped to calendar
    for tier in map[calendarName]:
        # if there is no event to be inserted to calendar, sikip
        if not tier in downtimeEvents: continue

        for event in downtimeEvents[tier]:
            #skip if event already inserted
            if event['summary'] in oldEvents[calendarId]:
                print 'Event is already in %s:' % calendarName, summary
                continue

            # insert new event
            createdEvent = service.events().insert(calendarId=i['id'], body=downtimeEvent).execute()
            print event['summary'], 'inserted...'
