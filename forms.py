from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import InputRequired
from config import country_ids

class CountryForm(FlaskForm):
    country = SelectField('Country', validators = [InputRequired()], 
        choices = country_ids.keys())
    submit = SubmitField('Submit')