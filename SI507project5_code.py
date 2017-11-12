import webbrowser
import json
import requests
import requests_oauthlib
from functools import reduce
import csv
from eb_data import CLIENT_ID, CLIENT_SECRET, personal_token
import sys
from datetime import datetime

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
AUTHORIZATION_URL = 'https://www.eventbrite.com/oauth/authorize'
TOKEN_URL = 'https://www.eventbrite.com/oauth/token'
REDIRECT_URI = 'https://www.programsinformationpeople.org/runestone/oauth'

HARVEY_CACHE_FNAME = "harvey_cache_contents.json"
CONCERT_CACHE_FNAME = "concert_cache_contents.json"

#--------------------------------------------------
# Load cache files: data and credentials
#--------------------------------------------------
# Load data cache
def check_if_cached(fname):
    try:
        with open(fname, 'r') as cache_file:
            cache_json = cache_file.read()
            CACHE_DICTION = json.loads(cache_json)
    except:
        CACHE_DICTION = {}
    return CACHE_DICTION

def has_cache_expired(timestamp_str, expire_in_days):
    """Check if cache timestamp is over expire_in_days old"""
    # gives current datetime
    now = datetime.now()

    # datetime.strptime converts a formatted string into datetime object
    cache_timestamp = datetime.strptime(timestamp_str, DATETIME_FORMAT)

    # subtracting two datetime objects gives you a timedelta object
    delta = now - cache_timestamp
    delta_in_days = delta.days

    # now that we have days as integers, we can just use comparison
    # and decide if cache has expired or not
    if delta_in_days > expire_in_days:
        return True # It's been longer than expiry time
    else:
        return False

# This is just for testing
HARVEY_CACHE_DICTION = check_if_cached(HARVEY_CACHE_FNAME)
CONCERT_CACHE_DICTION = check_if_cached(CONCERT_CACHE_FNAME)

def get_saved_token():
    with open('token.json', 'r') as f:
        token_json = f.read()
        token_dict = json.loads(token_json)

        return token_dict


def save_token(token_dict, expire_in_days):
    token_dict['timestamp'] = datetime.now().strftime(DATETIME_FORMAT)
    token_dict['expire_in_days'] = expire_in_days
    with open('token.json', 'w') as f:
        token_json = json.dumps(token_dict)
        f.write(token_json)


def get_eventbrite_cache(search_params, CACHE_FNAME, expire_in_days=7, force_download=False):
    CACHE_DICTION = check_if_cached(CACHE_FNAME)
    token_expired = False
    # if we need to get an oauth2 session started
    if CACHE_DICTION == {} or force_download:
        # see if we have the token
        try:
            token = get_saved_token()
        except FileNotFoundError:
            token = None

        if token:
            if not has_cache_expired(token['timestamp'], token['expire_in_days']):
                print('Token already saved and not expired')
                oauth2inst = requests_oauthlib.OAuth2Session(CLIENT_ID, token=token)
            else:
                print('token has expired, will need to get a new one')
                token_expired=True

        if token is None or token_expired:
            print('Getting token the long way')
            oauth2inst = requests_oauthlib.OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URI) # Create an instance of an OAuth2Session

            # get the authorization url to send the user to
            authorization_url, state = oauth2inst.authorization_url(AUTHORIZATION_URL)

            # Opening auth URL for you to sign in to the EventBrite service
            webbrowser.open(authorization_url) 
            authorization_response = input('Authenticate and then enter the full callback URL: ').strip() # Need to get the full URL in order to parse the response

            # The OAuth2Session instance has a method that extracts what we need from the url, and helps do some other back and forth with EB
            token = oauth2inst.fetch_token(TOKEN_URL, authorization_response=authorization_response, client_secret=CLIENT_SECRET)
            save_token(token, expire_in_days=expire_in_days)
        


        print('Token saved. Getting search results')
        r = oauth2inst.get('https://www.eventbriteapi.com/v3/events/search/', params=search_params)

        # the result is now a dictionary
        response_diction = json.loads(r.text)
        with open(CACHE_FNAME, 'w') as cache_file:
            print('caching result as:', CACHE_FNAME)
            for event in response_diction['events']:
                CACHE_DICTION[event['id']] = event
            cache_json = json.dumps(CACHE_DICTION, indent=2)
            cache_file.write(cache_json)
    else:
        print("{} already saved as cache, will return it".format(CACHE_FNAME))
    
    return CACHE_DICTION




class Event(object):
    def __init__(self, event_dict):
        self.event = event_dict
        self.id = self.event.get('id')
        self.name = self.event.get('name', {}).get('text')

        self.capacity = self.event.get('capacity')
        self.url = self.event.get('url')
        self.is_free = self.event.get('is_free')
        self.description = self.event.get('description', {}).get('text')

        self.get_data()

    def get_data(self, key_list=[('id',), ('name', 'text'), ('capacity',),
                                 ('url',), ('is_free',),
                                 ('description', 'text')]):
        self.data = {}
        for key in key_list:
            try:
                self.data[','.join(key)] = reduce(dict.get, key, self.event)
            except:
                self.data[','.join(key)] = None

    def __str__(self):
        return "{0}: {1}".format(self.id, self.name)


def write_to_csv(event_list, filename):
    with open(filename, 'w') as outfile:
        outwriter = csv.writer(outfile, delimiter=',')
        keys = event_list[0].data.keys()
        header = list(keys)
        outwriter.writerow(header)

        for event in event_list:
            row = list(event.data.values())
            outwriter.writerow(row)


if __name__ == '__main__':
    try:
        force_download = sys.argv[1].lower() == 'true'
    except:
        force_download = False

    harvey_search_params = {'q':'Hurricane Harvey',
                            "location.address":'6100 Main St, Houston, TX 77005',
                            'location.within':'30mi'}
    concert_search_params = {'q':'concert',
                             'location.address': "500 S State St, Ann Arbor, MI 48109",
                             'location.within':'20mi'}

    harvey_response = get_eventbrite_cache(harvey_search_params, 
                                           HARVEY_CACHE_FNAME,
                                           force_download=force_download)

    concert_response = get_eventbrite_cache(concert_search_params,
                                            CONCERT_CACHE_FNAME,
                                            force_download=force_download)

    harvey_event_list = [Event(event_dict) for event_dict in harvey_response.values()]
    concert_event_list = [Event(event_dict) for event_dict in concert_response.values()]
    print('writing to csv')
    write_to_csv(harvey_event_list, 'harvey.csv')
    write_to_csv(concert_event_list, 'um_concert.csv')
