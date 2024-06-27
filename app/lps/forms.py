from datetime import date

from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, IntegerField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class DataRequiredNoFlags(DataRequired):
    """
    Clears the HTML field flags to disable client side validation to avoid validation errors if form is cancelled.
    """
    field_flags = ()


class AdditionalArtistForm(FlaskForm):
    additional_artist_particle = StringField('Artist Particle', validators=[Length(0, 20)])
    additional_artist = StringField('Additional Artist', validators=[Length(0, 40)])


class LPMetaForm(FlaskForm):
    """ Form to defining a LP """
    lp_title = StringField('LP Title', validators=[Length(0, 120)])
    lp_main_artist = StringField('Main Artist', validators=[Length(0, 40)])
    lp_additional_artists = FieldList(FormField(AdditionalArtistForm, separator='-'), min_entries=5, max_entries=5)
    lp_mixer = StringField('Mixer', validators=[Length(0, 40)])
    lp_classical_composer = StringField('Classical Composer', validators=[Length(0, 40)])
    lp_year = IntegerField('Year Of Release', validators=[DataRequiredNoFlags()], default=date.today().year)


class NewLPMetaForm(LPMetaForm):
    """ Form for creating a new LP"""
    submit = SubmitField('Add Tracks')
    cancel = SubmitField('Cancel')


class ModifyLPForm(LPMetaForm):
    """ Form for modifying a LP"""
    submit = SubmitField('Save')
    cancel = SubmitField('Cancel')


class SongForm(FlaskForm):
    """ Form for a song entry on a track """
    song_title = StringField('Song Title', validators=[Length(0, 60)])


class LPTrackForm(FlaskForm):
    """ Form for a track on an LP """
    track_name = StringField('Track Name', validators=[Length(0, 40)])
    track_mixer = StringField('Track Mixer', validators=[Length(0, 40)])
    track_songs = FieldList(FormField(SongForm), min_entries=30, max_entries=30)


class NewLPTrackForm(LPTrackForm):
    """ Form for a new track on an LP """
    add_track = SubmitField('Add Another Track')
    save = SubmitField('Save And Finish')
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
