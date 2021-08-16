# Imports
from __main__ import app
from flask import render_template, redirect, abort, request, session
from flask.helpers import make_response
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
        'scope': 'user-read-private user-read-email', 
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
    data = {
        'grant_type': 'authorization_code',
        'code': request.args.get('code'),
        'redirect_uri': REDIRECT_URI,
    }
    response = requests.post(TOKEN_URL, 
        auth = (CLIENT_ID, CLIENT_SECRET), 
        data = data
    )
    response_data = response.json()

    # If the request is not successful, abort
    if response.status_code != 200:
        abort(response.status_code)
    
    # Add the tokens to session, redirect to generate()
    session['access_token'] = response_data.get('access_token')
    session['refresh_token'] = response_data.get('refresh_token')
    return redirect('/generate')