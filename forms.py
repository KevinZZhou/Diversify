from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import InputRequired
import os
from json import loads

class CountryForm(FlaskForm):
    country = SelectField('Country', validators = [InputRequired()], 
        choices = loads(os.environ['COUNTRY_IDS']).keys())
    submit = SubmitField('Submit')

class GeneratePlaylistForm(FlaskForm):
    generate = SubmitField('Generate')

class AccountForm(FlaskForm):
    account = SubmitField('Switch Accounts')

class LandingForm(FlaskForm):
    landing = SubmitField('Go Back')