import requests
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import ticketmaster as tm

SP_CLIENT_ID = os.getenv("SP_CLIENT_ID")
SP_CLIENT_SECRET = os.getenv("SP_CLIENT_SECRET")
SP_REDIRECT_URI = "http://localhost:8888/callback"
TM_API_KEY = os.getenv("TM_API_KEY")



sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SP_CLIENT_ID,
                                               client_secret=SP_CLIENT_SECRET,
                                               redirect_uri=SP_REDIRECT_URI,
                                               scope="user-library-read"))

concerts = tm.get_ticketmaster_concerts()
artists = tm.get_artists_from_concerts(concerts)

print(len(artists))
