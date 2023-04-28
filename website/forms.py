from flask_wtf import FlaskForm
from wtforms import RadioField

class ChoiceForm(FlaskForm):
    choices = RadioField('Choices', choices=[], coerce=int)