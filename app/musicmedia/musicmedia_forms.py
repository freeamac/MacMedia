from datetime import date

from flask_wtf import FlaskForm
from wtforms import BooleanField, FieldList, Form, FormField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class DataRequiredNoFlags(DataRequired):
    """
    Clears the HTML field flags to disable client side validation to avoid validation errors if form is cancelled.
    """
    field_flags = ()


class AdditionalArtistForm(Form):
    additional_artist_particle = StringField('Artist Particle', validators=[Length(0, 20)])
    additional_artist_prequel = StringField('Prequel', validators=[Length(0, 20)])
    additional_artist_sequel = StringField('Sequel', validators=[Length(0, 20)])
    additional_artist = StringField('Artist Name', validators=[Length(0, 40)])


class MusicMediaMetaForm(FlaskForm):
    """ Form to defining Music Media meta data """
    title = StringField('Title', validators=[Length(1, 120)])
    main_artist = StringField('Main Artist', validators=[Length(0, 40)])
    additional_artists = FieldList(FormField(AdditionalArtistForm, separator='-'), min_entries=1, max_entries=5)
    mixer = StringField('Mixer', validators=[Length(0, 40)])
    classical_composer_1 = StringField('Classical Composer 1', validators=[Length(0, 40)])
    classical_composer_2 = StringField('Classical Composer 2', validators=[Length(0, 40)])
    year = IntegerField('Year Of Release', validators=[DataRequiredNoFlags()], default=date.today().year)


class NewMusicMediaMetaForm(MusicMediaMetaForm):
    """ Form for creating a new Music Media item """
    submit = SubmitField('Add Tracks')
    cancel = SubmitField('Cancel')


class ModifyMusicMediaMetaForm(MusicMediaMetaForm):
    """ Form for modifying a Music Media item """
    save = SubmitField('Save')
    save_and_modify_tracks = SubmitField('Save & Modify Tracks')
    modify_tracks = SubmitField('Modify Tracks')
    cancel = SubmitField('Cancel')


class SongForm(FlaskForm):
    """ Form for a song entry on a track """
    song_title = StringField('Song Title', validators=[Length(1, 60)])
    song_additional_artists = FieldList(FormField(AdditionalArtistForm, separator='-'), min_entries=1, max_entries=4)
    song_featured_in = StringField('Feat. In', validators=[Length(0, 40)])
    song_list_main_artist = BooleanField('List Main Artist?')
    song_classical_composer_1 = StringField('Classical Comp. 1', validators=[Length(0, 40)])
    song_classical_composer_2 = StringField('Classical Comp. 2', validators=[Length(0, 40)])
    song_classical_work = StringField('Classical Work', validators=[Length(0, 40)])
    song_country = StringField('Country', validators=[Length(0, 20)])
    song_year = StringField('Release Year', validators=[Length(0, 4)])
    song_mix = StringField('Mix', validators=[Length(0, 40)])
    song_parts = TextAreaField('Song Parts')


class ModifySongForm(SongForm):
    """ Modify a song entry on a track """
    previous_song = SubmitField('Go To Previous Song')
    insert_song = SubmitField('Insert New Song')
    append_new_song = SubmitField('Append New Song')
    delete_song = SubmitField('Delete Song')
    next_song = SubmitField('Go To Next Song')
    save = SubmitField('Save And Finish')
    cancel = SubmitField('Cancel')


class MusicMediaTrackForm(FlaskForm):
    """ Form for a track on a Music Media item """
    track_name = StringField('Track Name', validators=[Length(0, 40)])
    track_mixer = StringField('Track Mixer', validators=[Length(0, 40)])
    track_songs = FieldList(FormField(SongForm), min_entries=1, max_entries=30)


class NewMusicMediaTrackForm(MusicMediaTrackForm):
    """ Form for a new track on an Music Media item """
    add_track = SubmitField('Add Another Track')
    save = SubmitField('Save And Finish')
    cancel = SubmitField('Cancel')


class ModifyMusicMediaTrackForm(MusicMediaTrackForm):
    """ Form to modify song track of an Music Media item """
    new_track = BooleanField('Adding New Track')
    modify_next_track = SubmitField('Save And Modify Next Track')
    modify_songs = SubmitField('Save And Modify Track Songs')
    save = SubmitField('Save And Finish')
    cancel = SubmitField('Cancel')


class DeleteMusicMediaForm(FlaskForm):
    """ Form for deleting a Music Media item """
    title = StringField('Title', render_kw={'readonly': True})
    artists = StringField('Artist(s)', render_kw={'readonly': True})
    classical_composer_1 = StringField('Classical Composer 1', render_kw={'readonly': True})
    classical_composer_2 = StringField('Classical Composer 2', render_kw={'readonly': True})
    mixer = StringField('Mixer', render_kw={'readonly': True})
    year = StringField('Year Of Release', render_kw={'readonly': True})

    submit = SubmitField('Delete')
    cancel = SubmitField('Cancel Deletion')
