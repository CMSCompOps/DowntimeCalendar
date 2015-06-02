import sys, time, google, dashboard
from optparse import OptionParser
from lib import url, fileOps
try: import json
except ImportError: import simplejson as json

#if len(sys.argv) < 4:
#    sys.stderr.write('not enough parameter!\n')
#    sys.exit(1)

parser = OptionParser()
parser.add_option("-k", "--key",    dest="jsonKeyFile", help="Key FILE for google calendar API",       metavar="FILE")
parser.add_option("-m", "--map",    dest="mapFile",     help="Map FILE to matche tiers and calendars", metavar="FILE")
parser.add_option("-s", "--source", dest="source",      help="Calendar source url",                    metavar="URL")
parser.add_option("-r", "--range",  dest="range",       help="Time RANGE (window) in hours",           type="int")
(options, args) = parser.parse_args()

if not options.jsonKeyFile or not options.mapFile or not options.source or not options.range:
    sys.stderr.write('not enough argument. please run python main.py --help.\n')
    sys.exit(1)

# create google calendar api
api         = google.calendarAPI(options.jsonKeyFile)
# parse calendar-CMS site tier map file
map         = json.loads(fileOps.read(options.mapFile))
# calculate lower bound parameter for google calendar api
lowerBound  = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - options.range*60*60))
# get downtimes from dashboard and parse json
print 'get downtime entries from dashboard: %s' %  options.source
dashboardDT = dashboard.getDowntimes(options.source, lowerBound)
# get all calendar under the google account
calendars   = api.getCalendars()['items']

# delete all old events to flush the downtime calendar
for calendar in calendars:
    # if curret calendar is not important for us, skip it
    # !!! be careful, you dont want to delete events placed
    # in other calendars. just delete events placed in related
    # calendars and time range (window) !!!
    if not calendar['summary'] in map: continue

    print '%s: all events between %s and now will be deleted' % (calendar['summary'], lowerBound)

    for event in api.getEvents(calendar['id'], lowerBound):
        api.deleteEvent(calendar['id'], event['id'])
        print '- delete: %s' % event['summary']

# insert entries
for calendar in calendars:
    # skip if current calendar is not our destionation
    if not calendar['summary'] in map: continue

    # get tiers stated in the map file
    tiers = map[calendar['summary']]

    print '%s, tiers: %s' % (calendar['summary'], tiers)

    for tier in tiers:
        events = dashboardDT[tier]
        for event in events:
            api.insertEvent(calendar['id'], event)
            print '+ insert: %s' % event['summary']
