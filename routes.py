# Imports
from __main__ import app
from flask import render_template, redirect, abort, request, session
from flask.helpers import make_response
from random import random, sample
from datetime import date
from json import dumps
import requests
from secrets import choice
from string import ascii_letters, digits
from urllib.parse import urlencode
from config import *
from forms import *


# Routes
# Landing page with country input
@app.route('/', methods = ['POST', 'GET'])
def landing():
    # Create form for country input
    # If submitted, save 'Country' in session and redirect to country page
    form: FlaskForm = CountryForm()
    if form.validate_on_submit():
        session['Country'] = form.country.data
        return redirect('/country=' + form.country.data)
    
    # If authorization was rejected, return to landing page with an alert
    if 'alert' in session:
        session.pop('alert')
        return render_template('landing.html', 
            alert = True, 
            form = form, 
            countries = country_ids.keys()
        )

    # If not submitted, return the landing page with the form
    return render_template('landing.html', 
        form = form, 
        countries = country_ids.keys(),
    )

# Page displaying the Top 50 playlist for a particular country
@app.route('/country=<place>', methods = ['POST', 'GET'])
def country(place):
    # Create "forms" (i.e., buttons)
    generate: FlaskForm = GeneratePlaylistForm()
    account: FlaskForm = AccountForm()

    # Return the country page if the country input is valid, 404 error otherwise
    try: 
        return render_template('country.html', 
            generate = generate, 
            account = account, 
            country = place, 
            country_embed = EMBED_URL + country_ids[place]
        )
    except KeyError:
        abort(404)

# Handles Spotify account authorization
@app.route('/login', methods = ['POST', 'GET'])
def login():
    # Query to be sent for authorization
    data = {
        'client_id': CLIENT_ID, 
        'response_type': 'code', 
        'redirect_uri': REDIRECT_URI, 
        'state': ''.join(choice(ascii_letters + digits) for _ in range(16)), 
        'scope': 'user-read-private user-read-email playlist-modify-public', 
        'show_dialog': True
    }
    
    # Send the authorization request to Spotify
    response = make_response(redirect(f'{AUTH_URL}/?{urlencode(data)}'))
    response.set_cookie('spotify_auth_state', data['state'])
    return response

# Handles logging out/switching accounts
@app.route('/account', methods = ['POST', 'GET'])
def account():
    return redirect('https://accounts.spotify.com/en/logout')

# Redirects to different pages depending on the result of Spotify authorization
@app.route('/callback', methods = ['POST', 'GET'])
def callback():
    # For rejected authorization, add session['alert'], redirect to landing page
    if 'error' in request.args:
        session['alert'] = True
        return redirect('/')
    
    # Request access and refresh tokens
    response = requests.post(TOKEN_URL, 
        auth = (CLIENT_ID, CLIENT_SECRET), 
        data = {
            'grant_type': 'authorization_code',
            'code': request.args.get('code'),
            'redirect_uri': REDIRECT_URI,
        }
    )
    response_data = response.json()

    # If the request is not successful, abort
    if response.status_code != 200:
        abort(response.status_code)
    
    # Add the tokens to session, redirect to generate()
    session['access_token'] = response_data.get('access_token')
    session['refresh_token'] = response_data.get('refresh_token')
    return redirect('/generate=' + session['Country'])

# Function to help generate the playlist
@app.route('/generate=<place>', methods = ['POST', 'GET'])
def generate(place):
    # If a token can't be found, abort
    if 'access_token' not in session or 'refresh_token' not in session:
        abort(400)
    
    # Create form to redirect to landing page
    form: FlaskForm = LandingForm()
    if form.validate_on_submit():
        return redirect('/')

    # Get Top 50 playlist of track ids for the desired country
    headers: dict[str] = {'Authorization': f'Bearer {session["access_token"]}'}
    top_50 = requests.get(PLAYLISTS_URL + country_ids[session['Country']], 
        headers = headers, 
        params = {'fields': 'tracks.items(track(id))'}
    )

    # If the request is not successful, abort
    if top_50.status_code != 200:
        abort(top_50.status_code)
    
    # Get 5 random songs from the Top 50 playlist
    song_ids: list[str] = [
        entry['track']['id'] for entry in top_50.json()['tracks']['items']
    ]
    random_five: list[str] = sample(song_ids, 5)

    # Get recommendations based on the 5 randomly selected songs as a seed
    recommendations = requests.get(RECOMMENDATIONS_URL, 
        headers = headers, 
        params = {
            'limit': '50', 
            'seed_tracks': random_five,
        }
    )
    recommended_songs: list[str] = [
        entry['uri'] for entry in recommendations.json()['tracks']
    ]

    # Get Spotify account user id
    user_id: str = requests.get(ME_URL, headers = headers).json()['id']

    # Create an empty Spotify playlist
    today: str = str(date.today().strftime('%Y-%m-%d'))
    playlist_id: str = requests.post(USERS_URL + user_id + '/playlists', 
        headers = headers, 
        data = dumps({'name': f'Generated from {place} - {today}'})
    ).json()['id']

    # Add recommended songs to the created Spotify playlist
    headers.update({'Content-Type': 'application/json'})
    requests.post(PLAYLISTS_URL + playlist_id + '/tracks', 
        headers = headers, 
        data = dumps({'uris': recommended_songs})
    )

    return render_template('generate.html', 
        form = form, 
        country = place, 
        playlist_embed = EMBED_URL + playlist_id, 
    )