from collections import UserDict
from typing import Literal, get_args, Dict, Any, Set

from . import EdrModel, JsonDict

Iso639Alpha2LanguageCode = Literal[
    'aa', 'ab', 'ae', 'af', 'ak', 'am', 'an', 'ar', 'as', 'av', 'ay', 'az', 'ba', 'be', 'bg', 'bi', 'bm', 'bn', 'bo',
    'br', 'bs', 'ca', 'ce', 'ch', 'co', 'cr', 'cs', 'cu', 'cv', 'cy', 'da', 'de', 'dv', 'dz', 'ee', 'el', 'en', 'eo',
    'es', 'et', 'eu', 'fa', 'ff', 'fi', 'fj', 'fo', 'fr', 'fy', 'ga', 'gd', 'gl', 'gn', 'gu', 'gv', 'ha', 'he', 'hi',
    'ho', 'hr', 'ht', 'hu', 'hy', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'io', 'is', 'it', 'iu', 'ja', 'jv', 'ka',
    'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'kr', 'ks', 'ku', 'kv', 'kw', 'ky', 'la', 'lb', 'lg', 'li', 'ln',
    'lo', 'lt', 'lu', 'lv', 'mg', 'mh', 'mi', 'mk', 'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'na', 'nb', 'nd', 'ne', 'ng',
    'nl', 'nn', 'no', 'nr', 'nv', 'ny', 'oc', 'oj', 'om', 'or', 'os', 'pa', 'pi', 'pl', 'ps', 'pt', 'qu', 'rm', 'rn',
    'ro', 'ru', 'rw', 'sa', 'sc', 'sd', 'se', 'sg', 'sh', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 'sq', 'sr', 'ss', 'st',
    'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tr', 'ts', 'tt', 'tw', 'ty', 'ug', 'uk',
    'ur', 'uz', 've', 'vi', 'vo', 'wa', 'wo', 'xh', 'yi', 'yo', 'za', 'zh', 'zu'
]  # We could use pycountry here, but it's overkill for a single static list

VALID_LANGUAGE_CODES = get_args(Iso639Alpha2LanguageCode)


class LanguageMap(UserDict, EdrModel["LanguageMap"]):
    """
    A dictionary that only accepts valid language codes as keys and strings for values
    Used for providing translated values in multiple languages for things like labels and descriptions that are
    intended to be read by humans.
    """

    @classmethod
    def _prepare_json_for_init(cls, json_dict: JsonDict) -> JsonDict:
        return json_dict

    @classmethod
    def _get_allowed_json_keys(cls) -> Set[str]:
        return set(VALID_LANGUAGE_CODES)

    def to_json(self) -> Dict[str, Any]:
        return dict(**self)

    def __getitem__(self, key: str) -> str:
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: str):
        if key not in VALID_LANGUAGE_CODES:
            raise ValueError(f"{key!r} is not a valid ISO 639-1 language code")
        if not isinstance(value, str):
            raise ValueError(f"Value must be a str! key={key!r}; value={value!r}")

        return super().__setitem__(key, value)
