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
