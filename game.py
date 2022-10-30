from dataclasses import dataclass, field
from random import choices, randint
from itertools import cycle

from scoring import Score, score_hand, name_hand
from errors import HandSizeError, DiceRangeError
from setup import InputType, AbstractFactory


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

    def get_input(self) -> None:
        assert self.input_type == InputType.USER, "Should only get user input for a user-input roll."
        while True:
            dice_input = [int(c) for c in input("Enter the roll as space-separated integers: ").split()]
            try:
                self.roll(dice_input)
                break
            except HandSizeError as hse:
                if self.no_dice < hse.size:
                    print(f"Too many dice added, {hse.size} added but {self.no_dice} expected.")
                else:
                    print(f"Too few dice added, {hse.size} added but {self.no_dice} expected.")
            except DiceRangeError as dre:
                for bad_die in dre.dice:
                    print(f"Die {bad_die[0]} has value {bad_die[1]}; out of range (expected 1-6).")

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

    def score_breakdown(self) -> list[Score]:
        """Method to get the potential scoring options for the hand. Should return a list of tuples,
        containing the scores for each combo as well as the dice involved."""
        """ First, check if there are any combos of 6 dice:"""
        return score_hand(self.dice)

    def score_total(self) -> int:
        """
        Get the maximum score for a single roll.

        :return: tuple of (roll name, score)
        """
        return sum([score.value for score in self.score_breakdown()])

    def name_score(self) -> str:
        return name_hand(self.dice)


class Player:
    def __init__(self, name, dice_type, input_type, strategy=None):
        self.name = name
        self.dice_type = dice_type

        self.input_type = input_type
        self.strategy = strategy

        self.score = 0

        self.possible_scores = []
        self.decisions = []
        self.play_on = False

    def __hash__(self):
        return hash(self.name)

    def set_possible_scores(self, possible_scores: list[Score]):
        self.possible_scores = possible_scores

    def set_strategy(self, strategy: str):
        self.strategy = strategy

    def get_decisions(self):
        if not self.possible_scores:
            raise ValueError("No scores passed with which to make decision.")

        if len(self.possible_scores) == 1:
            raise ValueError("Single score is always banked; no decision to make.")

        if self.input_type == InputType.USER:
            self.get_user_decisions()
        self.get_com_decisions()

    def get_user_decisions(self):
        decision_map = {'b': True, 'r': False}
        decisions = []

        for score in self.possible_scores:
            while True:
                decision = input(f"Combo: {score}. Enter b for BANK or r for RE-ROLL: ")
                try:
                    decisions.append(decision_map[decision])
                    break
                except KeyError:
                    print("Bad input, you need to choose 'b' or 'r'.")

        self.decisions = decisions

    def get_com_decisions(self):
        match self.strategy:
            case "LAZY-BANK": self.decisions = [True] * len(self.possible_scores)
            case "RANDOM": self.decisions = [bool(randint(0, 1)) for _ in self.possible_scores]

    def get_play_on(self):
        if self.input_type == InputType.USER:
            self.user_play_on()
        self.com_play_on()

    def user_play_on(self):
        while True:
            play_on = input("Input r for roll again or e for end turn: ")
            if play_on in {'r', 'e'}:
                break
            else:
                print("Bad input, try again.")

        match play_on:
            case 'r': self.play_on = True
            case 'e': self.play_on = False

    def com_play_on(self):
        match self.strategy:
            case "LAZY-BANK": self.play_on = True
            case "RANDOM": self.play_on = bool(randint(0, 1))

    def bank_scores(self) -> tuple[int, list[int]]:
        """
        Decide and subsequently bank possible scores in a hand of Farkell. Should take the possible scores as input (of
        which there should always be at least 2, as a single score always gets banked) and return the score and the
        dice to bank.

        :return: tuple of the score, and the dice involved in the score.
        """
        # self.get_decisions()

        assert len(self.possible_scores) == len(self.decisions), "Different number of decisions and possible scores."

        score = 0
        dice_to_remove = []

        for possible_score, decision in zip(self.possible_scores, self.decisions):
            if decision:  # True means we have decided to bank the score
                score += possible_score[0]
                dice_to_remove += possible_score[1]

        return score, dice_to_remove

    def turn(self) -> int:
        """Function for user-controlled, real dice-input turn. Returns the score from the turn."""
        available_dice, bank = 6, 0

        while True:
            dice = Roll(self.dice_type, available_dice)
            dice.get_input()

            # possible_scores = dice.score_breakdown()
            self.set_possible_scores(dice.score_breakdown())

            if not self.possible_scores:  # if the player doesn't score, the turn ends and no score is added
                print("NO SCORE! TURN ENDS.")
                return 0
            elif len(self.possible_scores) == 1:  # with one score we ALWAYS bank
                score, dice_to_remove = self.possible_scores[0]
            else:
                self.get_decisions()
                score, dice_to_remove = self.bank_scores()

            print(Roll(InputType.COM, len(dice_to_remove), dice_to_remove).name_score())
            bank += score

            if len(dice_to_remove) == available_dice:
                print("ALL DICE SCORED, NEW DICE!")
                available_dice = 6
            else:
                available_dice -= len(dice_to_remove)

            self.get_play_on()

            if self.play_on:
                continue
            self.score += bank
            return bank


class Game:
    """Class for a game of Farkell."""
    def __init__(self,
                 dice_input: InputType = InputType.COM,
                 max_score: int = 10000,
                 entry_score: int = 500,
                 players: dict[str: (InputType | tuple[InputType, str])] = None):

        self.dice_input = dice_input
        self.max_score = max_score
        self.entry_score = entry_score

        assert len(players) == len(set(players)), "Player names must be unique."
        self.players = []  # dictionary that maps player_name: Player
        for name in players:
            if players[name] == InputType.USER:
                self.players.append(Player(name, self.dice_input, players[name]))
            else:
                self.players.append(Player(name, self.dice_input, *players[name]))

        self.current_player = self.players[0]
        self.final_player = None
        self.last_round = False

    # def extrn_turn(self, player_name, score) -> None:
    #     self.players[player_name].score += score

    def game_end(self) -> bool:
        if self.current_player == self.final_player:
            return True
        return False

    def play(self) -> None:
        final_player, prev_player = None, None
        print("******* Game of Farkell *******")
        print("\n")
        in_the_game = {player: False for player in self.players}  # have the players scored the initial threshold?

        for player in cycle(self.players):
            print(f"***** {player.name}'s turn: *****")

            turn_score = player.turn()

            if not in_the_game[player.name]:
                if turn_score > self.entry_score:
                    in_the_game[player.name] = True
                    player.score += turn_score
                else:
                    print("***** entry score failed! *****")
            else:
                player.score += turn_score

            if self.game_end():
                print("***** " + self.get_winner().name + " has won the game! *****")
                print(self.score_table())
                return

            if player.score >= self.max_score and not self.last_round:
                self.final_player = prev_player
                self.last_round = True
                print("***** The last round has begun! *****")
                print(f"***** Can anyone beat {player.name}'s score of {player.score}? *****")

            elif not self.last_round:
                prev_player = player  # only need to keep track of this if it's not the final round

            print(self.score_table())

    def get_winner(self) -> Player:
        return max(self.players, key=lambda x: x.score)

    def score_table(self) -> str:
        msg = "|"
        for player in self.players:
            msg += " " + player.name + " " * (9 - len(player.name)) + "|"
        msg += "\n|"
        for player in self.players:
            score_str = str(player.score)
            msg += " " + score_str + " " * (9 - len(score_str)) + "|"

        return msg


class GameMaker(AbstractFactory):
    def new_game(self, pkl_file=None, kwargs=None) -> Game:
        if self.input_type == InputType.USER:
            self.get_terminal_input()
            return Game(**self.game_args)

        self.set_defaults()

        if pkl_file:
            del self.game_args["players"]["Player 1"]  # don't want to include the default player
            self.get_from_pkl(pkl_file)

        if not kwargs:
            return Game(**self.game_args)

        for kwarg in kwargs:
            self.game_args[kwarg] = kwargs[kwarg]
        return Game(**self.game_args)
