from datetime import date

from flask_wtf import FlaskForm
from wtforms import IntegerField, IntegerRangeField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import CheckboxInput

from app.models import Media_Type_Enum

class DataRequiredNoFlags(DataRequired):
    """
    Clears the HTML field flags to disable client side validation to avoid validation errors if form is cancelled.
    """
    field_flags = ()


class NewDVDForm(FlaskForm):
    """ Form to define a new application """
    dvd_title = StringField('New DVD Movie Title', validators=[DataRequiredNoFlags(), Length(0, 120)])
    dvd_series = StringField('Movie Series', validators=[Length(0, 120)])
    dvd_year = IntegerField('Year Of Release', validators=[DataRequiredNoFlags()], default=date.today().year)
    dvd_set = StringField('From Set', validators=[Length(0, 120)])
    dvd_media_type = SelectField('DVD Type?', choices=[Media_Type_Enum.dvd.name.capitalize(), Media_Type_Enum.blueray.name.capitalize()])
    dvd_music_type = SelectField('Music DVD?', choices=['No', 'Yes'])
    dvd_music_artist = StringField('Music DVD Artist', validators=[Length(0,120)])

    submit = SubmitField('Create')
    cancel = SubmitField('Cancel')