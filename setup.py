from enum import Flag
from collections import namedtuple


class InputType(Flag):
    USER = False
    COM = True


class GameFactory:
    """Class that creates a ready-to-play and ready-to-test Game instance."""
