#!/bin/bash

# json key for the google api
jsonKey="cms-test-49641fc90d34.json"
# calendar-CMS site tier map file
map="calendarTierMap.input"
# calendar source
cSource="http://dashb-ssb.cern.ch/dashboard/request.py/getplotdata?columnid=121&batch=1&view=default"

python main.py $jsonKey $map $cSource
