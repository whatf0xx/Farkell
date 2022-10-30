from enum import Flag
from abc import ABC
from typing import TypedDict
import pickle


class InputType(Flag):
    USER = False
    COM = True


class AbstractFactory(ABC):
    """Class to create a game instance based on function arguments, terminal input or dictionary kwargs (JSON input
    in the future?)."""

    params = {"dice_input": InputType,
              "max_score": int,
              "entry_score": int,
              "players": dict  # TODO: implement internal type checking for the dictionary
              }

    defaults = [InputType.USER,
                10000,
                500,
                {"Player 1": InputType.USER}
                ]

    valid_strategies = ["RANDOM", "LAZY-BANK"]

    def __init__(self, input_type: InputType = InputType.USER):
        self.input_type = input_type
        self.game_args = {}

    def set_defaults(self):
        for param, default in zip(self.params, self.defaults):
            if param not in self.game_args:
                self.game_args[param] = default

    def get_terminal_input(self):
        """Get terminal-input data for the game."""
        """get the dice input type for the game:"""
        while True:
            match input("Enter REAL for real dice rolls or RNG for simulated dice: ").upper():
                case "REAL":
                    self.game_args["dice_input"] = InputType.USER
                    break
                case "RNG":
                    self.game_args["dice_input"] = InputType.COM
                    break
                case _:
                    print("Input not understood; try again.")

        """get the max score for the game:"""
        while True:
            try:
                self.game_args["max_score"] = int(input("Enter the victory score for the game: "))
                break
            except ValueError:
                print("Victory score must be an integer: try again.")

        """get the entry score for the game:"""
        while True:  # get the entry score
            try:
                self.game_args["entry_score"] = int(input("Enter the entry score for the game: "))
                break
            except ValueError:
                print("Entry score must be an integer: try again.")

        """get the players' names and whether or not they're human or computer controlled:"""
        self.game_args["players"] = {}
        str_input = ""
        while str_input != "start":
            name = input("Enter the player's name: ")
            input_type = input("Enter USER if the player is a person or COM for a computer-controlled player: ")
            match input_type:
                case "USER":
                    self.game_args["players"][name] = InputType.USER
                case "COM":
                    while True:
                        input_strategy = input("Enter the strategy that the bot should use: ")
                        if input_strategy in self.valid_strategies:
                            break
                        print(f"{input_strategy} is not a valid strategy, please choose a valid strategy.")
                    self.game_args["players"][name] = (InputType.COM, input_strategy)
                case _:
                    print("Unrecognised input type, try again.")
                    continue
            str_input = input("Enter to add another player, or type 'start' to begin the game: ").lower()

    def get_from_pkl(self, filepath):
        with open(filepath, 'rb') as file:
            pickle_dict = pickle.load(file)
        for entry in pickle_dict:
            if type(pickle_dict[entry]) == self.params[entry]:
                self.game_args[entry] = pickle_dict[entry]
            else:
                continue
