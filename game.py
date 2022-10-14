from dataclasses import dataclass
from random import choices

import scoring

Index = int


@dataclass
class HandSizeError(ValueError):
    size: int


@dataclass
class DiceRangeError(ValueError):
    dice: list[tuple[Index, int]]


@dataclass
class Roll:
    """
    Class for a roll on a given turn, to ensure that the roll is a legal combination of dice. Also provides
    functionality for gathering the rolled dice, from user input or from the random module.
    """
    size: int
    dice: list[int]

    def __init__(self, size: int = 6, dice: list[int] = None):
        self.size = size
        if not dice:
            self.dice = choices([1, 2, 3, 4, 5, 6], k=self.size)
        else:
            self.dice = dice
            self.check()

    def check(self):
        """Check that there are the correct number of dice."""
        no_dice = len(self.dice)
        if no_dice != self.size:
            raise HandSizeError(size=no_dice)

        """Check that the dice are within the expected range."""
        bad_dice = []
        for i, die in enumerate(self.dice):
            if die not in [1, 2, 3, 4, 5, 6]:
                bad_dice.append((i, die))
        if bad_dice:
            raise DiceRangeError(dice=bad_dice)

    def count(self) -> dict[int: int]:
        allowed_dice = range(1, 7)
        return {i: self.dice.count(i) for i in allowed_dice}

    def score(self) -> tuple[str, int]:
        match self.size:
            case 1: return scoring.score_single(self.dice[0])
            case 2: return scoring.score_2(self.dice)
            case 3: return scoring.score_3(self.count())
            case 4: return scoring.score_4(self.count())
            case 5: return scoring.score_5(self.count())
            case 6: return scoring.score_6(self.count())
            case _: raise HandSizeError(size=self.size)


@dataclass
class Hand:
    """

    """
    dice: Roll
    bank: int
