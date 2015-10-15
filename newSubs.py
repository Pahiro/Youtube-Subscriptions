#!/usr/bin/python

import time
import httplib2
import os
import sys
import pickle
from autoremote.autoremote import autoremote
from apiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

watcharray = []
listarray = []
sendlist = []
sentlist = []

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret. You can acquire an OAuth 2.0 client ID and client secret from
# the Google Developers Console at
# https://console.developers.google.com/.
# Please ensure that you have enabled the YouTube Data API for your project.
# For more information about using OAuth2 to access the YouTube Data API, see:
#   https://developers.google.com/youtube/v3/guides/authentication
# For more information about the client_secrets.json file format, see:
#   https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
CLIENT_SECRETS_FILE = "/home/scripts/client_secrets.json"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = """
WARNING: Please configure OAuth 2.0

To make this sample run you will need to populate the client_secrets.json file
found at:

   %s

with information from the Developers Console
https://console.developers.google.com/

For more information about the client_secrets.json file format, please visit:
https://developers.google.com/api-client-library/python/guide/aaa_client_secrets
""" % os.path.abspath(os.path.join(os.path.dirname(__file__),
                                   CLIENT_SECRETS_FILE))

print("Starting...")
# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's account, but not other types of account access.
YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
  message=MISSING_CLIENT_SECRETS_MESSAGE,
  scope=YOUTUBE_READONLY_SCOPE)

storage = Storage("%s-oauth2.json" % sys.argv[0])
credentials = storage.get()

if credentials is None or credentials.invalid:
  flags = argparser.parse_args()
  credentials = run_flow(flow, storage, flags)

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
  http=credentials.authorize(httplib2.Http()))

##MAIN PROGRAM

url = "http://autoremotejoaomgcd.appspot.com/AutoRemoteServer.html?key=APA91bGmDIpMzA68xh_TWckE_hwcHALu2D7xrB48M0UTR9WgXXNItONHkf-_eP2v-nnzb_oOjaRf0HEYJXKMBr1o22_r08Skdj2QEd0vy09ewZg2t8l77UV5X1r65v2Tt3ntmeMeftXl"
message = 'downloadyoutube=:=https://www.youtube.com/watch?v='
ar=autoremote(url)
#ar.register("S5")

# Retrieve the contentDetails part of the channel resource for the
# authenticated user's channel.
watch_response = youtube.channels().list(
  mine=True,
  part="contentDetails"
).execute()

for channel in watch_response["items"]:
    watched_list_id = channel["contentDetails"]["relatedPlaylists"]["watchHistory"]

watchlistitems_list_request = youtube.playlistItems().list(
    playlistId=watched_list_id,
    part="snippet",
    maxResults=10
  )

watchlistitems_list_response = watchlistitems_list_request.execute()

for watchlist_item in watchlistitems_list_response["items"]:
    watcharray.append(watchlist_item["snippet"]["resourceId"]["videoId"])

#print("Printing watch list...")
#for x in watcharray:
#    print(x)
h = httplib2.Http(".cache")

def read(channel_name):
    channels_response = youtube.channels().list(
        forUsername=channel_name,
        part="contentDetails"
    ).execute()

    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]#["watchHistory"]
    print("Videos in list %s" % uploads_list_id)
  # Retrieve the list of videos uploaded to the authenticated user's channel.
    playlistitems_list_request = youtube.playlistItems().list(
        playlistId=uploads_list_id,
        part="snippet",
        maxResults=5
    )
    playlistitems_list_response = playlistitems_list_request.execute()
    for playlist_item in playlistitems_list_response["items"]:
        listarray.append(playlist_item["snippet"]["resourceId"]["videoId"])

read("BlueXephos")
read("YogscastKim")
read("YogscastLalna")
read("YogscastSjin")
read("HatFilms")

readfile = open("/home/scripts/sentitems.p","r")
sentlist = pickle.load(readfile)
readfile.close()

for item in listarray:
    if item not in watcharray:
        if item not in sentlist:
            sendlist.append(item)
#            print(item)

if not sendlist:
	print("Nothing to send")
else:	
	print("Number of items ",len(sendlist))
	print("Sent Items:")
for item in sendlist:
    sentlist.append(item)
    ar.send(message+item)
    print(item)
    time.sleep(20)

writefile = open("/home/scripts/sentitems.p","w")
pickle.dump(sentlist,writefile)
writefile.close()
#Remove entries of watched list from uploads list.
#Send list to Android Phone


