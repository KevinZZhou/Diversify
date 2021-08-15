# Imports
from __main__ import app
from flask import render_template, redirect, session
from config import *
from forms import *


# Routes
@app.route('/', methods = ['POST', 'GET'])
def landing():
    # Create form for country input
    # If submitted, save 'Country' in session and redirect to country page
    form: FlaskForm = CountryForm()
    if form.validate_on_submit():
        session['Country'] = form.country.data
        return redirect('/country=' + form.country.data)
    
    # If not submitted, return the landing page with the form
    return render_template('landing.html', form = form, 
        countries = country_ids.keys()
    )