#!/bin/bash

cd $(dirname $(readlink -f "${BASH_SOURCE[0]}"))

# json key for the google api
jsonKey="DowntimeCalendarsV2-b6fdb0cd2db4.json"
# calendar-CMS site tier map file
map="calendarTierMap.input"
# time range for both (google calendar and dashboard)
range=336
# calendar source
sourceURL="http://dashb-ssb.cern.ch/dashboard/request.py/getplotdata?columnid=121&time=$range&batch=1"

python main.py --key $jsonKey --map $map --source $sourceURL --range $range
