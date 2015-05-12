#!/bin/bash

cd $(dirname $(readlink -f "${BASH_SOURCE[0]}"))

# json key for the google api
jsonKey="DowntimeCalendarsV2-6de026a7257d.json"
# calendar-CMS site tier map file
map="calendarTierMap.input"
# calendar source
sourceURL="http://dashb-ssb.cern.ch/dashboard/request.py/getplotdata?columnid=121&time=336&batch=1"

python main.py --key $jsonKey --map $map --source $sourceURL
