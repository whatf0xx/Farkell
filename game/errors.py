"""
Module that holds the errors that are useful for debugging problems in the game mechanics
"""
from dataclasses import dataclass


@dataclass
class HandSizeError(ValueError):
    size: int


@dataclass
class DiceRangeError(ValueError):
    dice: list[tuple[int, int]]
