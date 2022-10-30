from game import InputType, Game, GameMaker, Player


def test_pkl_basic_creation():
    maker = GameMaker(InputType.COM)
    sample_game = maker.new_game("basic_setup.pkl")
    assert isinstance(sample_game, Game)
    assert sample_game.dice_input == InputType.USER
    assert sample_game.max_score == 10000
    assert sample_game.entry_score == 500
    names = ["Harry", "Leonie"]
    for player, name in zip(sample_game.players, names):
        assert isinstance(player, Player)
        assert player.name == name
        assert player.dice_type == InputType.USER
        assert player.input_type == InputType.USER
        assert player.score == 0

def test_pkl_with_edit():
    maker = GameMaker(InputType.COM)
    sample_game = maker.new_game("basic_setup.pkl", {"max_score": 2000})
    assert isinstance(sample_game, Game)
    assert sample_game.max_score == 2000
