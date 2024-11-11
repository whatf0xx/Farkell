from setup import InputType
import pickle

game_args = {
    "dice_input": InputType.USER,
    "max_score": 10000,
    "entry_score": 500,
    "players": {"Harry": InputType.USER,
                "Leonie": InputType.USER}
}

with open("../basic_setup.pkl", "wb") as file:
    pickle.dump(game_args, file)
