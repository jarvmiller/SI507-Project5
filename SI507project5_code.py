## import statements
import webbrowser
import json
import requests
import requests_oauthlib
from functools import reduce
import csv
from eb_data import CLIENT_ID, CLIENT_SECRET, personal_token


AUTHORIZATION_URL = 'https://www.eventbrite.com/oauth/authorize'
TOKEN_URL = 'https://www.eventbrite.com/oauth/token'
REDIRECT_URI = 'https://www.programsinformationpeople.org/runestone/oauth'
## CACHING SETUP

CACHE_FNAME = "cache_contents.json"
CREDS_CACHE_FILE = "creds.json"

#--------------------------------------------------
# Load cache files: data and credentials
#--------------------------------------------------
# Load data cache
try:
    with open(CACHE_FNAME, 'r') as cache_file:
        cache_json = cache_file.read()
        CACHE_DICTION = json.loads(cache_json)
except:
    CACHE_DICTION = {}


## ADDITIONAL CODE for program should go here...
## Perhaps authentication setup, functions to get and process data, a class definition... etc.

def get_saved_token():
    with open('token.json', 'r') as f:
        token_json = f.read()
        token_dict = json.loads(token_json)

        return token_dict

def save_token(token_dict):
    with open('token.json', 'w') as f:
        token_json = json.dumps(token_dict)
        f.write(token_json)

def get_eventbrite_cache(search_params, force_download=False, CACHE_DICTION=CACHE_DICTION)
    if CACHE_DICTION == {} or force_download == True:
        # Set up sessions and so on to get data via OAuth2 protocol...
        try:
            token = get_saved_token()
        except FileNotFoundError:
            token = None

        if token and force_download==False:
            print('token already saved, just retrieved it')
            oauth2inst = requests_oauthlib.OAuth2Session(CLIENT_ID, token=token)
        else:
            print('getting token the long way')
            oauth2inst = requests_oauthlib.OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI) # Create an instance of an OAuth2Session

            # get the authorization url to send the user to
            authorization_url, state = oauth2inst.authorization_url(AUTHORIZATION_URL)

            webbrowser.open(authorization_url) # Opening auth URL for you to sign in to the Spotify service
            authorization_response = input('Authenticate and then enter the full callback URL: ').strip() # Need to get the full URL in order to parse the response

            # The OAuth2Session instance has a method that extracts what we need from the url, and helps do some other back and forth with spotify
            token = oauth2inst.fetch_token(TOKEN_URL, authorization_response=authorization_response, client_secret=CLIENT_SECRET)
            save_token(token)
        


        print('getting owned events after obtaining token')
        r = oauth2inst.get('https://www.eventbriteapi.com/v3/events/search/', params=EB_search_params)
        # takes r.text and makes it into a dictionary
        # print(r.text)
        response_diction = json.loads(r.text)
        # print(response_diction['events'], [event['id'] for event in response_diction['events']])
        # print(response_diction['events'][0]['id'])
        # print(json.dumps(response_diction, indent=2)) # See the response printed neatly -- uncomment

        with open(CACHE_FNAME, 'w') as cache_file:
            print('saving event json as', CACHE_FNAME)
            for event in response_diction['events']:
                CACHE_DICTION[event['id']] = event
            cache_json = json.dumps(CACHE_DICTION, indent=2)
            cache_file.write(cache_json)
    else:
        print('owned events already saved as cache')
    
    return CACHE_DICTION

harvey_search_params = {'q':'Hurricane Harvey', "location.address":'6100 Main St, Houston, TX 77005',
                            'location.within':'30mi'}

CACHE_DICTION = get_eventbrite_cache(harvey_search_params, "location.address":'6100 Main St, Houston, TX 77005',
                            'location.within':'30mi'})

class Event(object):
    def __init__(self, event_dict):
        self.event = event_dict
        self.id = self.event.get('id')
        self.name = self.event.get('name', {}).get('text')

        self.capacity = self.event.get('capacity')
        self.uri = self.event.get('resource_uri')
        self.is_free = self.event.get('is_free')
        self.description = self.event.get('description', {}).get('text')

        self.get_data()

    def get_data(self, key_list=[('id',), ('name', 'text'), ('capacity',),
                                 ('resource_uri',), ('is_free',),
                                 ('description', 'text')]):
        self.data = {}
        for key in key_list:
            try:
                self.data[','.join(key)] = reduce(dict.get, key, self.event)
            except:
                self.data[','.join(key)] = None
        # print(self.data)

    def __str__(self):
        return "{0}: {1}".format(self.id, self.name)

event_list = [Event(event_dict) for event_dict in CACHE_DICTION.values()]

# [event.get_data() for event in event_list]
def write_to_csv(event_list, filename):
    with open(filename, 'w') as outfile:
        outwriter = csv.writer(outfile, delimiter=',')
        keys = event_list[0].data.keys()
        header = list(keys)
        outwriter.writerow(header)

        for event in event_list:
            row = list(event.data.values())
            outwriter.writerow(row)

write_to_csv(event_list, 'harvey.csv')

# to do:
# make a separate cache file, one for harvey, one for A2 concerts
## Make sure to run your code and write CSV files by the end of the program.
