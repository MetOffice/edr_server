import itertools
import string
import unittest

import pycountry
import pytest

from edr_server.core.exceptions import InvalidEdrJsonError
from edr_server.core.models.i18n import VALID_LANGUAGE_CODES, LanguageMap

EXPECTED_VALID_LANG_CODES = tuple(language.alpha_2 for language in pycountry.languages if hasattr(language, "alpha_2"))
EXPECTED_INVALID_LANG_CODES = tuple(
    code
    for chars in itertools.combinations_with_replacement(string.ascii_lowercase, 2)
    if (code := "".join(chars)) not in EXPECTED_VALID_LANG_CODES)


def test_valid_language_codes_correct():
    """Test that the VALID_LANGUAGE_CODES constant contains only the expected codes and not duplicates"""
    assert sorted(list(VALID_LANGUAGE_CODES)) == sorted(list(EXPECTED_VALID_LANG_CODES))


class LanguageMapTest(unittest.TestCase):
    def test_to_json(self):
        """GIVEN a LanguageMap WHEN to_json() is called THEN the equivalent JSON is returned"""
        expected = {"en": "foo"}
        lang_map = LanguageMap(en="foo")

        actual = lang_map.to_json()

        self.assertEqual(expected, actual)

    def test_to_json_empty_dict(self):
        """GIVEN a LanguageMap with no values WHEN to_json() is called THEN an empty dict is returned"""
        expected = {}
        lang_map = LanguageMap()

        actual = lang_map.to_json()

        self.assertEqual(expected, actual)

    def test_from_json(self):
        """
        GIVEN a JSON dict representing a valid LanguageMap
        WHEN from_json() is called
        THEN the equivalent LanguageMap is returned
        """
        expected = LanguageMap(en="foo")
        json_dict = {"en": "foo"}

        actual = LanguageMap.from_json(json_dict)

        self.assertEqual(expected, actual)

    def test_from_json_empty_dict(self):
        """GIVEN an empty dict WHEN from_json() is called THEN a LanguageMap with no values is returned"""
        expected = LanguageMap()
        json_dict = {}

        actual = LanguageMap.from_json(json_dict)

        self.assertEqual(expected, actual)


@pytest.mark.parametrize("code", EXPECTED_VALID_LANG_CODES)
def test_language_map_init_accepts_valid_codes(code: str):
    LanguageMap({code: "foo"})


@pytest.mark.parametrize("invalid_code", EXPECTED_INVALID_LANG_CODES)
def test_language_map_init_rejects_invalid_codes(invalid_code: str):
    with pytest.raises(ValueError):
        LanguageMap({invalid_code: "foo"})


@pytest.mark.parametrize("invalid_code", [1, ("en", "fr"), None, object(), type(object()), type(object)], ids=repr)
def test_language_map_init_rejects_non_str_codes(invalid_code: str):
    with pytest.raises(ValueError):
        LanguageMap({invalid_code: "foo"})


@pytest.mark.parametrize("invalid_val", [1, ("en", "fr"), None, object(), type(object()), type(object)], ids=repr)
def test_language_map_init_rejects_non_str_values(invalid_val: str):
    with pytest.raises(ValueError):
        LanguageMap(en=invalid_val)


@pytest.mark.parametrize("code", EXPECTED_VALID_LANG_CODES)
def test_language_map_setattr_accepts_valid_codes(code: str):
    lang_map = LanguageMap()
    lang_map[code] = "foo"


@pytest.mark.parametrize("invalid_code", EXPECTED_INVALID_LANG_CODES)
def test_language_map_setattr_rejects_invalid_codes(invalid_code: str):
    with pytest.raises(ValueError):
        lang_map = LanguageMap()
        lang_map[invalid_code] = "foo"


@pytest.mark.parametrize("invalid_code", [1, ("en", "fr"), None, object(), type(object()), type(object)], ids=repr)
def test_language_map_setattr_rejects_non_str_codes(invalid_code: str):
    with pytest.raises(ValueError):
        lang_map = LanguageMap()
        lang_map[invalid_code] = "foo"


@pytest.mark.parametrize("invalid_val", [1, ("en", "fr"), None, object(), type(object()), type(object)], ids=repr)
def test_language_map_setattr_rejects_non_str_values(invalid_val: str):
    with pytest.raises(ValueError):
        lang_map = LanguageMap()
        lang_map["en"] = invalid_val


@pytest.mark.parametrize(
    "invalid_val", [1, ("en", "fr"), None, object(), type(object()), type(object), ("e", "n")], ids=repr)
def test_language_map_from_json_invalid_value(invalid_val):
    """
    GIVEN a dict containing a value that isn't a string
    WHEN from_json() is called
    THEN a InvalidEdrJsonError is raised
    """
    with pytest.raises(InvalidEdrJsonError):
        LanguageMap.from_json({"en": invalid_val})


@pytest.mark.parametrize(
    "invalid_key", [1, ("en", "fr"), None, object(), type(object()), type(object), ("e", "n")], ids=repr)
def test_from_json_invalid_lang_code(invalid_key):
    """
    GIVEN a dict containing a key that isn't a language code
    WHEN from_json() is called
    THEN an InvalidEdrJsonError is raised
    """
    with pytest.raises(InvalidEdrJsonError):
        LanguageMap.from_json({invalid_key: "foo"})
