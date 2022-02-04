from dataclasses import dataclass

from .core import Interface


@dataclass
class APIData:
    pass


@dataclass
class CapabilitiesData:
    title: str
    description: str
    keywords: list
    provider_name: str
    provider_url: str
    contact_email: str
    contact_phone: str
    contact_fax: str
    contact_hours: str
    contact_instructions: str
    contact_address: str
    contact_postcode: str
    contact_city: str
    contact_state: str
    contact_country: str


class API(Interface):
    pass


class Capabilities(Interface):
    pass


class Conformance(Interface):
    pass