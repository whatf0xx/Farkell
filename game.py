from dataclasses import dataclass
from random import choices
from enum import Flag

import scoring


class InputType(Flag):
    USER = False
    ARGS = True


@dataclass
class HandSizeError(ValueError):
    size: int


@dataclass
class DiceRangeError(ValueError):
    dice: list[tuple[int, int]]


@dataclass
class Roll:
    """
    Class for a roll on a given turn, to ensure that the roll is a legal combination of dice. Also provides
    functionality for gathering the rolled dice, from user input or from the random module.
    """
    size: int
    dice: list[int]

    def __init__(self, size: int = 6, dice: list[int] = None) -> None:
        self.size = size
        if not dice:
            self.dice = choices([1, 2, 3, 4, 5, 6], k=self.size)
        else:
            self.dice = dice
            self.check()

    def check(self) -> None:
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
        """
        Get the frequency of each dice in the roll.

        :return: dictionary of [die: occurrences] (both ints)
        """
        allowed_dice = range(1, 7)
        return {i: self.dice.count(i) for i in allowed_dice}

    def score_total(self) -> tuple[str, int]:
        """
        Get the maximum score for a single roll, and name the score.

        :return: tuple of (roll name, score)
        """
        match self.size:
            # TODO: There is so much repeated code here.
            case 1: return scoring.score_single(self.dice[0])
            case 2: return scoring.score_2(self.dice)
            case 3: return scoring.score_3(self.count())
            case 4: return scoring.score_4(self.count())
            case 5: return scoring.score_5(self.count())
            case 6: return scoring.score_6(self.count())
            case _: raise HandSizeError(size=self.size)

    def score_breakdown(self) -> list[tuple[int, list[int]]]:
        """Method to get the potential scoring options for the hand. Should return a list of tuples,
        containing the scores for each combo as well as the dice involved."""
        """ First, check if there are any combos of 6 dice:"""
        scoring_tuples = []
        no_dice = len(self.dice)
        if no_dice == 6:
            combo_6 = scoring.combo_of_6(list(self.count().values()))
            if combo_6[0]:
                return [(combo_6[1], self.dice)]  # if we have a combo of 6, we're done

        combos = scoring.score_combos(self.dice)
        if combos[1]:
            scoring_tuples.append(combos)
            remaining_dice = [dice for dice in self.dice if dice not in combos[1]]
        else:
            remaining_dice = self.dice

        misc = scoring.score_misc(remaining_dice)
        if misc:
            scoring_tuples += misc

        if scoring_tuples:
            scoring_tuples.sort()
            """N.B. scoring tuples are SORTED, based on the score of the combo."""
            return scoring_tuples
        return []


@dataclass
class Turn:
    """

    """
    roll: Roll
    possible_scores = list[tuple[int, list[int]]]
    no_dice: int = 6
    bank: int = 0

    def __init__(self, user_input: bool = False):
        if not user_input:
            self.roll = Roll()
        else:
            while True:
                try:
                    self.roll = Roll(self.no_dice, [int(c) for c in input().split()])
                    break
                except HandSizeError as hse:
                    if self.no_dice < hse.size:
                        print(f"Too many dice added, {hse.size} added but {self.no_dice} expected.")
                    else:
                        print(f"Too few dice added, {hse.size} added but {self.no_dice} expected.")
                except DiceRangeError as dre:
                    for bad_die in dre.dice:
                        print(f"Die {bad_die[0]} has value {bad_die[1]}; out of range (expected 1-6).")

        self.possible_scores = self.roll.score_breakdown()

    def bank_scores(self, input_type: InputType = InputType.USER, decisions: list[bool] = None) -> str:
        if not self.possible_scores:
            return "HAND SCORES 0!"

        if len(self.possible_scores) == 1:
            self.bank += self.possible_scores[0][0]
            self.no_dice -= len(self.possible_scores[0][1])
            return self.roll.score_total()[0]

        if input_type == InputType.USER:
            decisions = []
            decision_map = {'b': True, 'r': False}
            for score in self.possible_scores:
                while True:
                    decision = input(f"combo: {score}. Enter b for BANK or r for RE-ROLL: ")
                    try:
                        decisions.append(decision_map[decision])
                        break
                    except KeyError:
                        print("Bad input, you need to choose 'b' or 'r'.")

        if len(decisions) != len(self.possible_scores):
            raise ValueError("Not all possible scores have a corresponding decision.")

        dice_to_score = []
        for score, decision in zip(self.possible_scores, decisions):
            if decision:  # True means we have decided to bank the score
                self.bank += score[0]
                self.no_dice -= len(score[1])
                dice_to_score += score[1]

        return Roll(len(dice_to_score), dice_to_score).score_total()[0]

