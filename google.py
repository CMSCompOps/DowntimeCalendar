try: import json
except ImportError: import simplejson as json
from oauth2client.client import SignedJwtAssertionCredentials
from httplib2 import Http
from apiclient.discovery import build
from lib import fileOps

def getCredentials(jsonKey):
    jsonData    = json.loads(fileOps.read(jsonKey))
    privateKey  = jsonData['private_key']
    clientEmail = jsonData['client_email']
    scope       = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.readonly']
    credentials = SignedJwtAssertionCredentials(clientEmail, privateKey, scope)
    return credentials

def getService(credentials):
    httpAuth    = credentials.authorize(Http())
    return build('calendar', 'v3', http = httpAuth)

class calendarAPI:
    def __init__(self, jsonKey):
        self.__credentials = getCredentials(jsonKey)
        self.service       = getService(self.__credentials)

    def getCalendars(self):
        """returns all google clendars under the authorized service"""
        return self.service.calendarList().list().execute()

    def getEvents(self, calendarId_, lowerBound = None):
        """returns all events under the given calendar"""
        eventList = []
        pageToken = None
        while True:
            if lowerBound:
                events = self.service.events().list(calendarId=calendarId_, pageToken=pageToken, timeMin = lowerBound).execute()
            else:
                events = self.service.events().list(calendarId=calendarId_, pageToken=pageToken).execute()
            if 'items' in events: eventList.extend(events['items'])
            pageToken = events.get('nextPageToken')
            if not pageToken:
                break
        return eventList

    def deleteEvent(self, calendarId_, eventId_):
        """deletes given google calendar event"""
        self.service.events().delete(calendarId=calendarId_, eventId=eventId_).execute()

    def insertEvent(self, calendarId_, event):
        """inserts given event"""
        self.service.events().insert(calendarId=calendarId_, body=event).execute()
