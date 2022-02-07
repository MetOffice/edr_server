from dataclasses import dataclass

from .core import Interface


@dataclass
class ServiceData:
    description_url: str
    license_url: str
    terms_url: str


class Service(Interface):
    def data(self) -> ServiceData:
        return ServiceData