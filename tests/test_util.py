"""
Tests for the Util.py module

Note the naming convention I am attempting to follow is
a Python-y version of Roy Osherove's suggestion:

http://osherove.com/blog/2005/4/3/naming-standards-for-unit-tests.html
"""

import unittest
try:
    import util  # The code under test
except ImportError:
    import PROJ_NAME.util as util


class TestListToDictionary(unittest.TestCase):
    """
    Tests util.list_to_dict
    """

    def setUp(self):
        self.test_list = ['Water type: cloudy', 'Month: February']
        self.too_few_colons = ['Rocky Racoon fell back in his room', 'Favorite ice cream: Rocky Road']
        self.too_many_colons = ['There are : way too many: colons in here: help!']

    def test_empty_list_return_empty_dictionary(self):
        self.assertEqual(util.list_to_dict([]), {})

    def test_can_handle_extra_colons(self):
        self.assertEqual(util.list_to_dict(self.too_many_colons),
                         {'There_are_': 'way too many: colons in here: help!'})

    def test_can_handle_no_colons(self):
        self.assertEqual(util.list_to_dict(self.too_few_colons),
                         {'Favorite_ice_cream': 'Rocky Road'})


class TestCalcSoilAcres(unittest.TestCase):
    """
    Tests util.calc_soil_acres

    Note: I considered adding a test for the input being a list but did
    not because of the top-voted answer on this question:
    https://stackoverflow.com/questions/2645749

    I think this is worth documenting for myself that I shouldn't be writing
    tests to do typechecking on any arbitrary stupid input the caller (er, myself)
    might forget and put in.
    """

    def setUp(self):
        self.in_list_bad_acres = [{'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 83.1},
                                  {'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 13.2},
                                  {'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 'kitties'},
                                  {'Survey_Number': 121, 'Texture': 'LOAM', 'Acres': 'parrots'},
                                  {'Survey_Number': 121, 'Texture': 'LOAM', 'Acres': 'PROJ_NAME'}]

        self.in_list_null_and_none = [{'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 83.1},
                                  {'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 'Null'},
                                  {'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 'None'}]

        self.no_good_list = [{'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 'None'}]

    def test_nonnumeric_acres_dropped(self):
        self.assertEqual(util.calc_soil_acres(self.in_list_bad_acres),
                         [{'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 96.3}])

    def test_none_null_converted(self):
        self.assertEqual(util.calc_soil_acres(self.in_list_null_and_none),
                         [{'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 83.1}])

    def test_no_good_entries_returns_empty_list(self):
        self.assertEqual(util.calc_soil_acres(self.no_good_list), [])


class TestGroupSoilTextures(unittest.TestCase):
    """
    Tests util.group_soil_textures
    """
    def setUp(self):
        self.nonstring_texture = [{'Survey_Number': 301, 'Texture': 564, 'Acres': 83.1},
                                  {'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 83.1}]

        self.single_entry = [{'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 83.1}]

    def test_nonstring_texture_gets_converted(self):
        self.assertEqual(util.group_soil_textures(self.nonstring_texture),
                         [{'Survey_Number': 301, 'Texture': '564/COBBLE', 'Acres': 83.1}])

    def test_single_texture_doesnt_concat(self):
        self.assertEqual(util.group_soil_textures(self.single_entry),
                         [{'Survey_Number': 301, 'Texture': 'COBBLE', 'Acres': 83.1}])

    def test_empty_input_returns_empty_output(self):
        self.assertEqual(util.group_soil_textures([]), [])


class TestFormatSoils(unittest.TestCase):
    """
    Tests util.format_soils.
    """

    def setUp(self):
        self.with_duplicates = [['Survey Number: 3907', 'Texture: COBBLY LOAM', 'Acres: 94.88'],
                                ['Survey Number: 3907', 'Texture: COBBLY LOAM', 'Acres: 94.88']]
        self.with_none_texture = [['Survey Number: 3907', 'Texture: None', 'Acres: 94.88']]

    def test_dupes_removed(self):
        self.assertEqual(util.format_soils(self.with_duplicates),
                         [{'Survey_Number': '3907', 'Texture': 'COBBLY LOAM', 'Acres': 94.88}])

    def test_none_textures_removed(self):
        self.assertEqual(util.format_soils(self.with_none_texture), [])


class TestCheckCorporateTechniques(unittest.TestCase):
    """
    Tests util.check_corporate_techniques
    """

    def test_unknown_technique_raises_error(self):
        self.assertRaises(util.TimberSaleTechniqueError,
                          util.check_corporate_techniques,
                          {'Cutting_it_all_down'})

    def test_known_technique_does_not_raise_error(self):
        """If it process a known technique, default returns None"""
        self.assertEqual(util.check_corporate_techniques({'CLEAR_CUT'}), None)


if __name__ == '__main__':
    unittest.main()
