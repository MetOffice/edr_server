from collections import UserDict
from typing import Literal, get_args

IsoAlpha2LanguageCode = Literal[
    'ab', 'aa', 'af', 'ak', 'sq', 'am', 'ar', 'an', 'hy', 'as', 'av', 'ae', 'ay', 'az', 'bm', 'ba', 'eu', 'be', 'bn',
    'bi', 'bs', 'br', 'bg', 'my', 'ca', 'ch', 'ce', 'ny', 'zh', 'cu', 'cv', 'kw', 'co', 'cr', 'hr', 'cs', 'da', 'dv',
    'nl', 'dz', 'en', 'eo', 'et', 'ee', 'fo', 'fj', 'fi', 'fr', 'fy', 'ff', 'gd', 'gl', 'lg', 'ka', 'de', 'el', 'kl',
    'gn', 'gu', 'ht', 'ha', 'he', 'hz', 'hi', 'ho', 'hu', 'is', 'io', 'ig', 'id', 'ia', 'ie', 'iu', 'ik', 'ga', 'it',
    'ja', 'jv', 'kn', 'kr', 'ks', 'kk', 'km', 'ki', 'rw', 'ky', 'kv', 'kg', 'ko', 'kj', 'ku', 'lo', 'la', 'lv', 'li',
    'ln', 'lt', 'lu', 'lb', 'mk', 'mg', 'ms', 'ml', 'mt', 'gv', 'mi', 'mr', 'mh', 'mn', 'na', 'nv', 'nd', 'nr', 'ng',
    'ne', 'no', 'nb', 'nn', 'ii', 'oc', 'oj', 'or', 'om', 'os', 'pi', 'ps', 'fa', 'pl', 'pt', 'pa', 'qu', 'ro', 'rm',
    'rn', 'ru', 'se', 'sm', 'sg', 'sa', 'sc', 'sr', 'sn', 'sd', 'si', 'sk', 'sl', 'so', 'st', 'es', 'su', 'sw', 'ss',
    'sv', 'tl', 'ty', 'tg', 'ta', 'tt', 'te', 'th', 'bo', 'ti', 'to', 'ts', 'tn', 'tr', 'tk', 'tw', 'ug', 'uk', 'ur',
    'uz', 've', 'vi', 'vo', 'wa', 'cy', 'wo', 'xh', 'yi', 'yo', 'za', 'zu'
]

VALID_LANGUAGE_CODES = get_args(IsoAlpha2LanguageCode)


class LanguageMap(UserDict):
    """
    A dictionary that only accepts valid language codes as keys and strings for values
    Used for providing translated values in multiple languages for things like labels and descriptions that are
    intended to be read by humans.
    """

    def __getitem__(self, key: str) -> str:
        return super().__getitem__(key)

    def __setitem__(self, key: str, value: str):
        if key not in VALID_LANGUAGE_CODES:
            raise ValueError(f"{key!r} is not a valid ISO 639-1 language code")
        if not isinstance(value, str):
            raise ValueError(f"Value must be a str! value={value!r}")

        return super().__setitem__(key, value)
