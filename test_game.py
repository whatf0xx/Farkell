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


def test_bot_creation():
    maker = GameMaker(InputType.COM)
    players = {
        "Harry": InputType.USER,
        "Leonie": InputType.USER,
        "Bot 1": (InputType.COM, "RANDOM"),
        "Bot 2": (InputType.COM, "LAZY-BANK")
    }
    sample_game = maker.new_game("basic_setup.pkl", {"players": players})
    assert isinstance(sample_game, Game)
    assert sample_game.players[2].input_type == InputType.COM
    assert sample_game.players[2].strategy == "RANDOM"
    assert sample_game.players[3].input_type == InputType.COM
    assert sample_game.players[3].strategy == "LAZY-BANK"
