import unittest

import pytest

from app.musicmedia.musicmedia_objects import (
    Artists,
    AdditionalArtist,
    CASSETTEs,
    CDs,
    ELPs,
    LPs,
    MINI_CDs,
    MediaType,
    MediaException
)

from app.musicmedia.route_utilities import (
    append_new_artists,
    append_new_additional_artists,
    build_additional_artist_tuples,
    build_classical_composer_names_tuple,
    get_macmedia_library,
    field_value_or_none,
    massage_particle_or_sequel,
    name_value_or_blank,
)


class MuscmediaRouteUtilitiesTestCase(unittest.TestCase):

    def test_get_macmedia_library(self):
        """ Test all possible media libraries and exception """

        test_media_type = MediaType.CASSETTE
        self.assertEqual(get_macmedia_library(test_media_type), CASSETTEs)

        test_media_type = MediaType.CD
        self.assertEqual(get_macmedia_library(test_media_type), CDs)

        test_media_type = MediaType.ELP
        self.assertEqual(get_macmedia_library(test_media_type), ELPs)

        test_media_type = MediaType.LP
        self.assertEqual(get_macmedia_library(test_media_type), LPs)

        test_media_type = MediaType.MINI_CD
        self.assertEqual(get_macmedia_library(test_media_type), MINI_CDs)

        with pytest.raises(MediaException):
            test_media_type = 'DVDs'
            _ = get_macmedia_library(test_media_type)

    def test_massage_particle_or_sequel(self):
        """ Test particle and sequel messaging """

        self.assertEqual(massage_particle_or_sequel(None), '')
        self.assertEqual(massage_particle_or_sequel(''), '')
        self.assertEqual(massage_particle_or_sequel('.'), ' . ')
        self.assertEqual(massage_particle_or_sequel(','), ', ')

    def test_field_value_or_none(self):
        """ Test extracting field values from form data """

        class data_value():
            pass

        title_value = data_value()
        setattr(title_value, 'data', '')
        artist_value = data_value()
        setattr(artist_value, 'data', 'New Artist')
        test_form_field = {'title': title_value, 'artist': artist_value}

        # ToDo: Requires changes in route_utilities.py. See ToDo there
        # self.assertIsNone(field_value_or_none(test_form_field, 'mix'))

        self.assertIsNone(field_value_or_none(test_form_field, 'title'))

        setattr(title_value, 'data', None)
        self.assertIsNone(field_value_or_none(test_form_field, 'title'))

        setattr(title_value, 'data', 'New Title')
        self.assertEqual(field_value_or_none(test_form_field, 'title'), test_form_field['title'].data)
        self.assertEqual(field_value_or_none(test_form_field, 'artist'), test_form_field['artist'].data)

    def test_name_value_or_blank(self):
        """ Test artist name or blank function """

        class data_value():
            name = None

        self.assertEqual(name_value_or_blank(None), '')

        test_data_value = data_value
        data_value.name = 'New artist'
        self.assertEqual(name_value_or_blank(test_data_value), test_data_value.name)

    def test_build_additional_artist_tuples(self):
        """ Ensure artist tuples are constructed correctly """

        artist_info, artists_prequels, artists_names, artists_sequels = build_additional_artist_tuples(None)
        self.assertEqual(artist_info, [])
        self.assertEqual(artists_prequels, tuple([]))
        self.assertEqual(artists_names, tuple([]))
        self.assertEqual(artists_sequels, tuple([]))

        artist_info, artists_prequels, artists_names, artists_sequels = build_additional_artist_tuples([])
        self.assertEqual(artist_info, [])
        self.assertEqual(artists_prequels, tuple([]))
        self.assertEqual(artists_names, tuple([]))
        self.assertEqual(artists_sequels, tuple([]))

        artist_1 = AdditionalArtist(Artists.create_Artist('First Artist'), sequel=',')
        artist_2 = AdditionalArtist(Artists.create_Artist('Second Artist'), prequel='with', sequel='and')
        artist_3 = AdditionalArtist(Artists.create_Artist('Third Artist'), prequel='lastly')
        additional_artists = [artist_1, artist_2, artist_3]
        expected_artists_info = [{'additional_artist_prequel': '', 'additional_artist': 'First Artist', 'additional_artist_sequel': ','},
                                 {'additional_artist_prequel': 'with', 'additional_artist': 'Second Artist', 'additional_artist_sequel': 'and'},
                                 {'additional_artist_prequel': 'lastly', 'additional_artist': 'Third Artist', 'additional_artist_sequel': ''}]
        expected_prequels = ('', 'with', 'lastly')
        expected_names = ('First Artist', 'Second Artist', 'Third Artist')
        expected_sequels = (',', 'and', '')
        artist_info, artists_prequels, artists_names, artists_sequels = build_additional_artist_tuples(additional_artists)
        self.assertEqual(expected_artists_info, artist_info)
        self.assertEqual(expected_prequels, artists_prequels)
        self.assertEqual(expected_names, artists_names)
        self.assertEqual(expected_sequels, artists_sequels)

    def test_build_classical_composers_name_tuple(self):
        """ Test classical composers names tuple """

        self.assertEqual(build_classical_composer_names_tuple(None), tuple([]))
        self.assertEqual(build_classical_composer_names_tuple([]), tuple([]))

        classical_composer_1 = Artists.create_Artist('Bach')
        classical_composer_2 = Artists.create_Artist('Strauss')
        composers_name_tuple = build_classical_composer_names_tuple([classical_composer_1, classical_composer_2])
        self.assertEqual(composers_name_tuple, ('Bach', 'Strauss'))

        # Check order is applied correctly
        composers_name_tuple = build_classical_composer_names_tuple([classical_composer_2, classical_composer_1])
        self.assertEqual(composers_name_tuple, ('Strauss', 'Bach'))

    def test_append_new_artists(self):
        """ Check creating and adding a new artist to an artist list """

        artist_list = []
        new_artist_name_list_1 = ['Bon Jovi']
        new_lp = LPs.create(MediaType.LP, 'Slippery When Wet', year=1984, artists=[Artists.create_Artist('Various Artists')])

        new_artist_list = append_new_artists(artist_list, new_artist_name_list_1, new_lp)
        # Note that create_Artist() does not create a new artist if they already exist
        self.assertEqual(new_artist_list, [Artists.create_Artist('Bon Jovi')])

        new_artist_list = append_new_artists(new_artist_list, [], new_lp)
        # Note that create_Artist() does not create a new artist if they already exist
        self.assertEqual(new_artist_list, [Artists.create_Artist('Bon Jovi')])

        new_artist_name_list_2 = ['Queen', 'Rolling Stones']
        new_artist_list = append_new_artists(new_artist_list, new_artist_name_list_2, new_lp)
        # Note that create_Artist() does not create a new artist if they already exist
        self.assertEqual(new_artist_list, [Artists.create_Artist('Bon Jovi'), Artists.create_Artist('Queen'), Artists.create_Artist('Rolling Stones')])

    def test_append_new_additional_artists(self):
        """ Check creating and adding new additional artists to an additional artists list """

        self.assertEqual(append_new_additional_artists(None, [], [], [], None), [])

        additional_artist_list = []
        new_lp = LPs.create(MediaType.LP, 'Slippery When Wet', year=1984, artists=[Artists.create_Artist('Various Artists')])
        additional_artist_list = append_new_additional_artists(additional_artist_list, ['Bon Jovi'], [None], [None], new_lp)
        self.assertEqual(1, len(additional_artist_list))
        added_additional_artist = additional_artist_list[0]
        # Note that create_Artist() does not create a new artist if they already exist
        self.assertEqual(added_additional_artist.artist, Artists.create_Artist('Bon Jovi'))
        self.assertEqual(added_additional_artist.prequel, '')
        self.assertEqual(added_additional_artist.sequel, '')

        additional_artist_list = append_new_additional_artists(additional_artist_list,
                                                               ['Queen', 'Rolling Stones'],
                                                               ['with', 'lastly'],
                                                               ['and', None],
                                                               new_lp)
        self.assertEqual(3, len(additional_artist_list))
        artists_in_list = [additional_artist_list[0].artist, additional_artist_list[1].artist, additional_artist_list[2].artist]
        expected_artists_in_list = [Artists.create_Artist('Bon Jovi'), Artists.create_Artist('Queen'), Artists.create_Artist('Rolling Stones')]
        self.assertEqual(expected_artists_in_list, artists_in_list)
        prequels_in_list = [additional_artist_list[0].prequel, additional_artist_list[1].prequel, additional_artist_list[2].prequel]
        expcted_prequels_in_list = ['', 'with', 'lastly']
        self.assertEqual(expcted_prequels_in_list, prequels_in_list)
        sequels_in_list = [additional_artist_list[0].sequel, additional_artist_list[1].sequel, additional_artist_list[2].sequel]
        expcted_sequels_in_list = ['', 'and', '']
        self.assertEqual(expcted_sequels_in_list, sequels_in_list)
