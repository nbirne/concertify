import requests
from dotenv import load_dotenv
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import date, timedelta

load_dotenv()

SP_CLIENT_ID = os.getenv("SP_CLIENT_ID")
SP_CLIENT_SECRET = os.getenv("SP_CLIENT_SECRET")
SP_REDIRECT_URI = "http://localhost:8888/callback"
TM_API_KEY = os.getenv("TM_API_KEY")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SP_CLIENT_ID,
                                               client_secret=SP_CLIENT_SECRET,
                                               redirect_uri=SP_REDIRECT_URI,
                                               scope="playlist-modify-private"))

def get_ticketmaster_concerts():
    print("Getting ticketmaster concerts." + TM_API_KEY)
    print("API key:" + TM_API_KEY)
    
    base_url = "https://app.ticketmaster.com/discovery/v2/events"
    city = "Boston"
    date_range_start = date.today()
    date_range_end = date_range_start + timedelta(days=60)  # Two months from today

    params = {
        "city": city,
        "startDateTime": date_range_start.strftime("%Y-%m-%dT00:00:00Z"),
        "endDateTime": date_range_end.strftime("%Y-%m-%dT23:59:59Z"),
        "classificationName": 'Music',
        "apikey": TM_API_KEY
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Check for any request errors
        data = response.json()
        events = data["_embedded"]["events"]
        print(f"Found {len(events)} events.")
        return events
    except requests.exceptions.RequestException as e:
        print("Error connecting to the API:", e)
        return []

def print_concerts(concerts):
    if concerts:
        print("Concerts in Boston within the next two months:")
        print(f"Count: {len(concerts)}")
        for concert in concerts:
            name = concert['name']
            date = concert['dates']['start']['localDate']
            url = concert['url']
            
            # Get the performer's name from the attractions field
            performers = [attraction['name'] for attraction in concert['_embedded']['attractions']]
            performers_str = ', '.join(performers)
            
            print(f"{name} - {date} - {performers_str} - {url}")
    else:
        print("No concerts found.")

def get_artists_from_concerts(concerts):
    print("Getting artists from concert list.")
    artists = set()
    for concert in concerts:
        # Get the performer's name from the attractions field
        concert_artists = [attraction['name'] for attraction in concert['_embedded']['attractions']]
        artists.update(concert_artists)
    print(f"Found {len(artists)} artists.")
    return artists

def get_artist_songs(artist_names):
    artist_songs = {}
    
    for artist_name in artist_names:
        # Search for the artist on Spotify
        results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)

        if results['artists']['items']:
            artist = results['artists']['items'][0]
            artist_id = artist['id']

            # Get the top tracks for the artist
            top_tracks = sp.artist_top_tracks(artist_id)

            if top_tracks['tracks']:
                # Take the first three tracks as the most popular ones
                popular_songs = [track['name'] for track in top_tracks['tracks'][:3]]
                artist_songs[artist_name] = popular_songs
            else:
                artist_songs[artist_name] = ["No popular songs found"]
        else:
            artist_songs[artist_name] = ["Artist not found"]

    return artist_songs

concerts = get_ticketmaster_concerts()
artists = get_artists_from_concerts(concerts)
songs = get_artist_songs(artists)
print(songs)