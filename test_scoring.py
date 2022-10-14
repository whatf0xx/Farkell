import pickle
import game

with open("rolls-scores.pkl", "rb") as file:
    rolls = pickle.load(file)


def test():
    for roll in rolls:
        inputted = rolls[roll]
        calculated = game.Roll(6, roll).score()[1]
        assert_msg = f"Roll of {roll}; inputted score: {inputted}, calculated score: {calculated}."
        assert inputted == calculated, assert_msg
