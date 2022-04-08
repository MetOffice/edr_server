"""This class belongs in models, but I had to move it out to break a circular import loop"""
from enum import Enum


class EdrDataQuery(Enum):
    CUBE = "cube"
    CORRIDOR = "corridor"
    LOCATIONS = "locations"
    ITEMS = "items"
    AREA = "area"
    POSITION = "position"
    RADIUS = "radius"
    TRAJECTORY = "trajectory"
