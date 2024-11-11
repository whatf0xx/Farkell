import pickle
import game

with open("rolls-scores.pkl", "rb") as file:
    rolls = pickle.load(file)


def test_score():
    for roll in rolls:
        inputted = rolls[roll][0]
        calculated = game.Roll(game.InputType.USER, 6, roll).score_total()
        assert_msg = f"Roll of {roll}; inputted score: {inputted}, calculated score: {calculated}."
        assert inputted == calculated, assert_msg


def test_get_score():
    for roll in rolls:
        inputted = sorted(rolls[roll][1], key=lambda x: x[0])
        calculated = sorted(game.Roll(game.InputType.USER, 6, roll).score_breakdown(), key=lambda x: x[0])
        assert_msg = f"Roll of {roll};\ninputted breakdown: {inputted}, calculated breakdown: {calculated}."
        assert inputted == calculated, assert_msg
