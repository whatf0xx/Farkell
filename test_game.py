from game import InputType, Game, GameMaker


def test_creation():
    sample_game = GameMaker(InputType.COM).new_game("basic_setup.pkl")
    assert isinstance(sample_game, Game)
