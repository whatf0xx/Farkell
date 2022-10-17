from dataclasses import dataclass
from random import choices
from enum import Flag
from itertools import cycle

import scoring


class InputType(Flag):
    USER = False
    COM = True


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
        # TODO: Roll.__init__() needs to be brought into line with Turn.__init__().
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
    input_type = InputType.COM
    no_dice: int = 6
    bank: int = 0

    def __init__(self, no_dice: int = 6, input_type: InputType = InputType.USER, bank: int = 0):
        self.no_dice = no_dice
        self.input_type = input_type
        self.bank = bank
        if input_type == InputType.COM:
            self.roll = Roll(size=self.no_dice)
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

    def reroll(self):
        if self.no_dice == 0:
            self.__init__(6, self.input_type, self.bank)

        self.__init__(self.no_dice, self.input_type, self.bank)


@dataclass
class Player:
    name: str
    input_type: InputType
    score: int


@dataclass
class Game:
    players: list[Player]
    max_score: int = 10000
    last_round: bool = False

    def __init__(self, player_names: list[str], player_types: list[InputType] = None, max_score: int = 10000):
        self.players = []
        if not player_types:
            player_types = [InputType.USER] * len(player_names)
        else:
            assert len(player_names) == len(player_types)

        for name, player_type in zip(player_names, player_types):
            self.players.append(Player(name, player_type, 0))

        self.max_score = max_score

    def score_table(self):
        msg = "|"
        for player in self.players:
            msg += " " + player.name + " " * (9 - len(player.name)) + "|"
        msg += "\n|"
        for player in self.players:
            msg += " " + str(player.score) + " " * (9 - len(str(player.score))) + "|"

        return msg

    def play(self) -> None:
        final_player, prev_player = None, None
        for player in cycle(self.players):
            # TODO: Need to have the condition that it's the players' first turn.
            print(f"***** {player.name}'s turn: *****")
            turn = Turn(no_dice=6, input_type=player.input_type, bank=0)
            while True:
                turn.bank_scores()
                # TODO: If this returns no possible scores, turn should end.
                # TODO: If a 6-dice combo is achieved, this should automatically roll over.
                while True:
                    play_on = input("Input r for roll again or e for end turn: ")
                    if play_on == 'r' or 'e':
                        break
                    else:
                        print("Bad input, try again,")
                match play_on:
                    case 'r':
                        turn.reroll()
                    case 'e':
                        player.score += turn.bank
                        break

            if player == final_player:
                print("*****" + self.get_winner().name + " has won the game! *****")
                print(self.score_table())
                return

            if player.score >= self.max_score and not self.last_round:
                final_player = prev_player
                self.last_round = True
                print("***** The last round has begun! *****")
                print(f"***** Can anyone beat {player.name}'s score of {player.score}? *****")

            elif not self.last_round:
                prev_player = player  # only need to keep track of this if it's not the final round

            print(self.score_table())

    def get_winner(self):
        return max(self.players, key=lambda x: x.score)
