from flask import Flask, render_template, redirect, request, session, url_for
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='views')
app.secret_key = os.urandom(24)

# Spotify API credentials
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI', 'http://localhost:5000/callback')

# Spotify scopes
SCOPE = 'user-read-currently-playing user-read-playback-state'

@app.route('/')
def index():
    if 'token_info' not in session:
        return redirect(url_for('login'))
    
    sp = spotipy.Spotify(auth=session['token_info']['access_token'])
    try:
        current_track = sp.current_playback()
        if current_track is None:
            return render_template('home.html', error="No track currently playing")
        
        track_info = {
            'name': current_track['item']['name'],
            'artist': current_track['item']['artists'][0]['name'],
            'album': current_track['item']['album']['name'],
            'image_url': current_track['item']['album']['images'][0]['url'] if current_track['item']['album']['images'] else None
        }
        return render_template('home.html', track=track_info)
    except Exception as e:
        return render_template('home.html', error=str(e))

@app.route('/login')
def login():
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE
    )
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SCOPE
    )
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
