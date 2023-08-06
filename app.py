import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, request, session, redirect
from flask_session import Session
from functions import get_ticketmaster_concerts, print_concerts, get_artists_from_concerts, get_songs_from_artists, get_saved_tracks

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

SP_CLIENT_ID = os.getenv("SP_CLIENT_ID")
SP_CLIENT_SECRET = os.getenv("SP_CLIENT_SECRET")
SP_REDIRECT_URI = "http://127.0.0.1:5000/"
TM_API_KEY = os.getenv("TM_API_KEY")
SCOPE = "playlist-modify-private user-library-read"

@app.route("/", methods=["GET", "POST"])
def index():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    sp_oauth = SpotifyOAuth(client_id=SP_CLIENT_ID, client_secret=SP_CLIENT_SECRET, redirect_uri=SP_REDIRECT_URI, scope=SCOPE, cache_handler=cache_handler)
    
    if request.args.get("code"):
        # Step 2. Being redirected from Spotify auth page
        sp_oauth.get_access_token(request.args.get("code"))
        return redirect('/')

    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        # Step 1. Display sign in link when no token
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    sp_client = spotipy.Spotify(oauth_manager=sp_oauth)

    if request.method == "POST":
        city = request.form["city"]

        concerts = get_ticketmaster_concerts(city)
        artists = get_artists_from_concerts(concerts)
        songs = get_songs_from_artists(sp_client, artists)

        return render_template("result.html", artists=artists, songs=songs)
    
    return render_template("form.html")

@app.route("/login")
def login():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    
    # Create the SpotifyOAuth instance
    sp_oauth = SpotifyOAuth(client_id=SP_CLIENT_ID, client_secret=SP_CLIENT_SECRET, redirect_uri=SP_REDIRECT_URI, scope=SCOPE, cache_handler=cache_handler)
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    # Get the authorization URL
    auth_url = sp_oauth.get_authorize_url()

    # Redirect the user to the Spotify login page
    return redirect(auth_url)

@app.route("/callback")
def callback():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    
    # Get the SpotifyOAuth instance
    sp_oauth = SpotifyOAuth(client_id=SP_CLIENT_ID, client_secret=SP_CLIENT_SECRET, redirect_uri=SP_REDIRECT_URI, scope=SCOPE, cache_handler=cache_handler)
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return redirect('/')

    # Get the access token from the callback URL
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)

    # Store the access token in the session
    session["spotify_token"] = token_info["access_token"]

    return redirect("/")

@app.route('/sign_out')
def sign_out():
    session.pop("token_info", None)
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)