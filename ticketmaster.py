import requests
from datetime import date, timedelta
import os

def get_ticketmaster_concerts():
    print("Getting ticketmaster concerts.")
    
    base_url = "https://app.ticketmaster.com/discovery/v2/events"
    city = "Boston"
    date_range_start = date.today()
    date_range_end = date_range_start + timedelta(days=60)  # Two months from today

    params = {
        "apikey": os.getenv("TM_API_KEY"),
        "city": city,
        "startDateTime": date_range_start.strftime("%Y-%m-%dT00:00:00Z"),
        "endDateTime": date_range_end.strftime("%Y-%m-%dT23:59:59Z"),
        "classificationName": 'Music',
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
    
concerts = get_ticketmaster_concerts()
get_artists_from_concerts(concerts)
