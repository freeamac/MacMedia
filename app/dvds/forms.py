from datetime import date

from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from app.models import Media_Type_Enum


class DataRequiredNoFlags(DataRequired):
    """
    Clears the HTML field flags to disable client side validation to avoid validation errors if form is cancelled.
    """
    field_flags = ()


class DVDForm(FlaskForm):
    """ Form to defining a DVD """
    dvd_title = StringField('DVD Movie Title', validators=[DataRequiredNoFlags(), Length(0, 120)])
    dvd_series = StringField('Movie Series', validators=[Length(0, 120)])
    dvd_year = IntegerField('Year Of Release', validators=[DataRequiredNoFlags()], default=date.today().year)
    dvd_set = StringField('From Set', validators=[Length(0, 120)])
    dvd_media_type = SelectField('DVD Type?', choices=[Media_Type_Enum.dvd.name.capitalize(), Media_Type_Enum.blueray.name.capitalize()])
    dvd_music_type = SelectField('Music DVD?', choices=['No', 'Yes'])
    dvd_music_artist = StringField('Music DVD Artist', validators=[Length(0, 120)])


class NewDVDForm(DVDForm):
    """ Form for creating a new DVD"""
    submit = SubmitField('Create')
    cancel = SubmitField('Cancel')


class ModifyDVDForm(DVDForm):
    """ Form for modifying a DVD"""
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')


class DeleteDVDForm(FlaskForm):
    """ Form for deleting a DVD"""
    dvd_title = StringField('DVD Movie Title', render_kw={'readonly': True})
    dvd_series = StringField('Movie Series', render_kw={'readonly': True})
    dvd_year = StringField('Year Of Release', render_kw={'readonly': True})
    dvd_set = StringField('From Set', render_kw={'readonly': True})
    dvd_media_type = SelectField('DVD Type?', render_kw={'readonly': True})
    dvd_music_type = StringField('Music DVD?', render_kw={'readonly': True})
    dvd_music_artist = StringField('Music DVD Artist', render_kw={'readonly': True})

    submit = SubmitField('Delete')
    cancel = SubmitField('Cancel Deletion')
