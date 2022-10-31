import unittest
from edr_server.core.models.i18n import LanguageMap
from edr_server.core.models.parameters import Unit

class UnitTest(unittest.TestCase):

    def test_from_json(self):
        """
        GIVEN a Unit with a LanguageMap label
        WHEN from_json() is called
        THEN the expected Unit is returned
        Added in response to this conversation:
        https://github.com/MetOffice/edr_server/pull/35#discussion_r1008271136
        """
        expected = Unit(labels={"en": "foo"})

        unit = Unit(labels=LanguageMap(en="foo"))
        json_dict = {'label': {"en": "foo"}}

        actual = unit.from_json(json_dict)

        self.assertEqual(expected, actual)