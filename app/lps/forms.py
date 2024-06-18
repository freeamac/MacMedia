from datetime import date

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app.models import Location_Type_Enum, Media_Type_Enum


class DataRequiredNoFlags(DataRequired):
    """
    Clears the HTML field flags to disable client side validation to avoid validation errors if form is cancelled.
    """
    field_flags = ()


class LPForm(FlaskForm):
    """ Form to defining a LP """
    lp_title = StringField('LP Title', validators=[DataRequiredNoFlags(), Length(0, 120)])
    lp_artists = StringField('Artist(s)', validators=[Length(0, 120)])
    lp_year = IntegerField('Year Of Release', validators=[DataRequiredNoFlags()], default=date.today().year)
    lp_set = StringField('From Set', validators=[Length(0, 120)])
    lp_media_type = SelectField('LP Type?', choices=[Media_Type_Enum.dvd.name.capitalize(), Media_Type_Enum.blueray.name.capitalize()])
    lp_music_type = SelectField('Music LP?', choices=['No', 'Yes'])
    lp_music_artist = StringField('Music LP Artist', validators=[Length(0, 120)])
    lp_location = SelectField('LP Location?', choices=[Location_Type_Enum.home.name.capitalize(), Location_Type_Enum.away.name.capitalize()])


class NewLPForm(LPForm):
    """ Form for creating a new LP"""
    submit = SubmitField('Create')
    cancel = SubmitField('Cancel')


class ModifyLPForm(LPForm):
    """ Form for modifying a LP"""
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')


class DeleteLPForm(FlaskForm):
    """ Form for deleting a LP"""
    lp_title = StringField('LP Title', render_kw={'readonly': True})
    lp_artists = StringField('Artist(s)', render_kw={'readonly': True})
    lp_composer = StringField('Classical Composer', render_kw={'readonly': True})
    lp_mixer = StringField('Mixer', render_kw={'readonly': True})
    lp_year = StringField('Year Of Release', render_kw={'readonly': True})

    submit = SubmitField('Delete')
    cancel = SubmitField('Cancel Deletion')
