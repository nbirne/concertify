import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)

# Set the secret key to use sessions in Flask
app.secret_key = os.getenv("SESSION_SECRET_KEY")

SP_CLIENT_ID = os.getenv("SP_CLIENT_ID")
SP_CLIENT_SECRET = os.getenv("SP_CLIENT_SECRET")
SP_REDIRECT_URI = "http://127.0.0.1:5000/callback"
TM_API_KEY = os.getenv("TM_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    if "spotify_token" not in session:
        print("need token")
        return redirect("/login")

    if request.method == "POST":
        city = request.form["city"]
        result = city
        return render_template("result.html", result=result)
    return render_template("form.html")

@app.route("/login")
def login():
    # Create the SpotifyOAuth instance
    sp_oauth = SpotifyOAuth(client_id=SP_CLIENT_ID, client_secret=SP_CLIENT_SECRET, redirect_uri=SP_REDIRECT_URI, scope=["playlist-modify-private"])

    # Get the authorization URL
    auth_url = sp_oauth.get_authorize_url()

    # Redirect the user to the Spotify login page
    return redirect(auth_url)

@app.route("/callback")
def callback():
    # Get the SpotifyOAuth instance
    sp_oauth = SpotifyOAuth(client_id=SP_CLIENT_ID, client_secret=SP_CLIENT_SECRET, redirect_uri=SP_REDIRECT_URI, scope=["playlist-modify-private"])

    # Get the access token from the callback URL
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)

    # Store the access token in the session
    session["spotify_token"] = token_info["access_token"]

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)