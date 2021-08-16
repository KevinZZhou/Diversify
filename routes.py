# Imports
from __main__ import app
from flask import render_template, redirect, abort, session
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
    
    # If not submitted, return the landing page with the form
    return render_template('landing.html', 
        form = form, 
        countries = country_ids.keys(),
    )

# Page displaying the Top 50 for a particular country
@app.route('/country=<place>', methods = ['POST', 'GET'])
def country(place):
    generate: FlaskForm = GeneratePlaylistForm()
    account: FlaskForm = AccountForm()
    try: 
        return render_template('country.html', 
            generate = generate, 
            account = account, 
            country = place, 
            playlist_link = country_ids[place]
        )
    except KeyError:
        abort(404)
