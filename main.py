#  ____      _         ___  
# |  _ \ ___| |_ _ __ / _ \ 
# | |_) / _ \ __| '__| | | |
# |  _ <  __/ |_| |  | |_| |
# |_| \_\___|\__|_|   \___/ 

# Libraries
import pandas as pd
from speech_recognition import Microphone, Recognizer, UnknownValueError
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth

from pepper import *

print(" ____      _         ___  ")
print("|  _ \ ___| |_ _ __ / _ \ ")
print("| |_) / _ \ __| '__| | | |")
print("|  _ <  __/ |_| |  | |_| |")
print("|_| \_\___|\__|_|   \___/ ")

"""
To run this script, you must have a file in this directory called 'setup.txt'
In this file, enter all of the values of the required variables in the following format:

client_id=XXXXXXXX
client_secret=XXXXXXX
device_name=XXXXXXXX
redirect_uri=https://example.com/callback/
username=XXXXXXXXXXXXXX
scope=user-read-private user-read-playback-state user-modify-playback-state
"""

# Set variables from setup.txt
setup = pd.read_csv('setup.txt', sep='=', index_col=0, squeeze=True, header=None)
client_id = setup['client_id']
client_secret = setup['client_secret']
device_name = setup['device_name']
redirect_uri = setup['redirect_uri']
scope = setup['scope']
username = setup['username']
print(client_id)

# Connecting to the Spotify account
auth_manager = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    username=username)
spotify = sp.Spotify(auth_manager=auth_manager)

# Selecting device to play from
devices = spotify.devices()
deviceID = None
for d in devices['devices']:
    d['name'] = d['name'].replace('’', '\'')
    if d['name'] == device_name:
        deviceID = d['id']
        break

# Setup microphone and speech recognizer
r = Recognizer()
m = Microphone()
input_mic = Microphone()

while True:
    """
    Commands will be entered in the specific format explained here:
     - the first word will be one of: 'album', 'artist', 'play'
     - then the name of whatever item is wanted
    """
    with m as source:
        r.adjust_for_ambient_noise(source=source)
        audio = r.listen(source=source)

    command = None
    try:
        command = r.recognize_google(audio_data=audio).lower()
    except UnknownValueError:
        continue

    print(command)
    words = command.split()
    if len(words) <= 1:
        print('Could not understand. Try again')
        continue

    name = ' '.join(words[1:])
    
    try:
        if words[0] == 'album':
            uri = get_album_uri(spotify=spotify, name=name)
            play_album(spotify=spotify, device_id=deviceID, uri=uri)
        elif words[0] == 'artist':
            uri = get_artist_uri(spotify=spotify, name=name)
            play_artist(spotify=spotify, device_id=deviceID, uri=uri)
        elif words[0] == 'play':
            uri = get_track_uri(spotify=spotify, name=name)
            play_track(spotify=spotify, device_id=deviceID, uri=uri)
        else:
            print('Specify either "album", "artist" or "play". Try Again')
    except InvalidSearchError:
        print('InvalidSearchError. Try Again')
