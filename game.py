from dataclasses import dataclass, field
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
    input_type: InputType = InputType.COM
    no_dice: int = 6
    """N.B. the default 'roll' of dice should be an empty list which is then populated with the Roll.roll() method."""
    dice: list[int] = field(default_factory=list)

    def roll(self, dice: list[int] = None) -> None:
        if self.input_type == InputType.COM:
            self.dice = choices([1, 2, 3, 4, 5, 6], k=self.no_dice)
        else:
            self.dice = dice
            self.check()

    def remove_dice(self, dice_to_remove) -> None:
        self.no_dice -= dice_to_remove

    def check(self) -> None:
        """Check that there are the correct number of dice."""
        no_dice = len(self.dice)
        if no_dice != self.no_dice:
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
        match self.no_dice:
            # TODO: There is so much repeated code here.
            case 1: return scoring.score_single(self.dice[0])
            case 2: return scoring.score_2(self.dice)
            case 3: return scoring.score_3(self.count())
            case 4: return scoring.score_4(self.count())
            case 5: return scoring.score_5(self.count())
            case 6: return scoring.score_6(self.count())
            case _: raise HandSizeError(size=self.no_dice)

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
class Player:
    name: str
    position: int  # where the player is 'sat' in the circle, not how well he is doing etc.
    input_type: InputType
    score: int


class Game:
    setup: InputType  # if COM, then expects game parameters passed to Game.__init__(), else get_game_data() is called
    dice_input = InputType  # if COM, use an RNG; if USER, take input of the dice that are rolled
    players: dict[str: Player]  # map player names to player
    # TODO: keeping the players list as a dictionary introduces a lot of problems later
    max_score: int
    first_score: int
    last_round: bool = False

    def __init__(self, input_type: InputType = InputType.USER, dice_input: InputType = InputType.COM,
                 player_dict: dict[str: InputType] = None, max_score: int = 10000, entry_score: int = 500):
        self.setup = input_type
        if self.setup == InputType.COM:
            self.dice_input = dice_input
            self.players = {}
            for i, player in enumerate(player_dict):
                self.players[player] = (Player(player, i+1, player_dict[player], 0))  # count from 1 for humans
            self.max_score = max_score
            self.entry_score = entry_score
        else:
            self.get_game_data()

    def get_game_data(self) -> None:
        """Get terminal-input data for the game."""
        """get the dice input type for the game:"""
        while True:
            match input("Enter REAL for real dice rolls or RNG for simulated dice: ").upper():
                case "REAL":
                    self.dice_input = InputType.USER
                    break
                case "RNG":
                    self.dice_input = InputType.COM
                    break
                case _:
                    print("Input not understood; try again.")

        """get the max score for the game:"""
        while True:
            try:
                self.max_score = int(input("Enter the victory score for the game: "))
                break
            except ValueError:
                print("Victory score must be an integer: try again.")

        """get the entry score for the game:"""
        while True:  # get the entry score
            try:
                self.entry_score = int(input("Enter the entry score for the game: "))
                break
            except ValueError:
                print("Entry score must be an integer: try again.")

        """get the players' names and whether or not they're human or computer controlled:"""
        self.players = {}
        str_input = ""
        i = 1
        while str_input != "start":
            name = input("Enter the player's name: ")
            input_type = input("Enter USER if the player is a person or COM for a computer-controlled player: ")
            match input_type:
                case "USER":
                    self.players[name] = Player(name, i, InputType.USER, 0)
                case "COM":
                    self.players[name] = Player(name, i, InputType.COM, 0)
                case _:
                    print("Bad input; player creation failed: try again.")
                    continue
            str_input = input("Enter to add another player, or type 'start' to begin the game: ").lower()
            i += 1

    def extrn_turn(self, player_name, score) -> None:
        self.players[player_name].score += score

    # def iterate_players(self) -> str:
    #     i = 1  # humans count from 1
    #     player_name = next(player.name for player in self.players if self.players[player].position == i)
    #     while True:
    #         yield player_name
    #         i = 2 + (i-1) % len(self.players)
    #         player_name = next(player.name for player in self.players if self.players[player].position == i)

    def play(self) -> None:
        final_player, prev_player = None, None
        print("******* Game of Farkell *******")
        print("\n")
        in_the_game = {player: False for player in self.players}  # have the players scored the initial threshold?

        for name in cycle(self.players):
            player = self.players[name]
            print(f"***** {player.name}'s turn: *****")

            turn_score = turn()  # see below

            if not in_the_game[player.name]:
                if turn_score > self.entry_score:
                    in_the_game[player.name] = True
                    player.score += turn_score
                else:
                    print("***** entry score failed! *****")
            else:
                player.score += turn_score

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
        return max(self.players.values(), key=lambda x: x.score)

    def score_table(self):
        msg = "|"
        for player in self.players:
            msg += " " + self.players[player].name + " " * (9 - len(self.players[player].name)) + "|"
        msg += "\n|"
        for player in self.players:
            score_str = str(self.players[player].score)
            msg += " " + score_str + " " * (9 - len(score_str)) + "|"

        return msg


def bank_scores(possible_scores: list[tuple[int, list[int]]],
                input_type: InputType = InputType.USER, decisions: list[bool] = None) -> tuple[int, int]:
    if not possible_scores:
        print("NO SCORE")
        return 0, 0

    if len(possible_scores) == 1:
        print("-Return the name of the scored combo-")
        return possible_scores[0][0], len(possible_scores[0][1])

    if input_type == InputType.USER:
        decisions = []
        decision_map = {'b': True, 'r': False}
        for score in possible_scores:
            while True:
                decision = input(f"Combo: {score}. Enter b for BANK or r for RE-ROLL: ")
                try:
                    decisions.append(decision_map[decision])
                    break
                except KeyError:
                    print("Bad input, you need to choose 'b' or 'r'.")

    assert len(possible_scores) == len(decisions), "Different number of decisions and possibilities."

    score = 0
    dice_to_remove = []

    for possible_score, decision in zip(possible_scores, decisions):
        if decision:  # True means we have decided to bank the score
            score += possible_score[0]
            dice_to_remove += possible_score[1]

    print("-Return the name of the scored combo-")
    return score, len(dice_to_remove)


# TODO: Currently, this can't accept paramter decisions to pass to bank_scores()
def turn() -> int:
    """Function for user-controlled, real dice-input turn. Returns the score from the turn."""
    available_dice, bank = 6, 0

    while True:
        dice = Roll(InputType.USER, available_dice)
        """Get the dice roll as user input, and handle the error cases:"""
        while True:
            dice_input = [int(c) for c in input("Enter the roll as space-separated integers: ").split()]
            try:
                dice.roll(dice_input)
                break
            except HandSizeError as hse:
                if dice.no_dice < hse.size:
                    print(f"Too many dice added, {hse.size} added but {dice.no_dice} expected.")
                else:
                    print(f"Too few dice added, {hse.size} added but {dice.no_dice} expected.")
            except DiceRangeError as dre:
                for bad_die in dre.dice:
                    print(f"Die {bad_die[0]} has value {bad_die[1]}; out of range (expected 1-6).")

        possible_scores = dice.score_breakdown()
        score, dice_to_remove = bank_scores(possible_scores)
        if not possible_scores:  # if the player doesn't score, the turn ends and no score is added
            return 0

        bank += score
        if dice_to_remove == available_dice:
            print("ALL DICE SCORED, NEW DICE!")
            available_dice = 6
        else:
            available_dice -= dice_to_remove

        while True:
            play_on = input("Input r for roll again or e for end turn: ")
            if play_on in {'r', 'e'}:
                break
            else:
                print("Bad input, try again.")

        match play_on:
            case 'r':
                continue
            case 'e':
                return bank
