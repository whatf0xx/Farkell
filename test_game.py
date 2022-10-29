from game import InputType, Game


def test_bank_scores():
    sample_game = Game(InputType.COM, InputType.USER, {"Harry": InputType.COM}, 10000, 500)
    sample_game.players["Harry"].set_possible_scores([[50, [5]], [50, [5]]])
    sample_game.players["Harry"].set_strategy("LAZY-BANK")
    sample_game.players["Harry"].get_decisions()
    assert len(sample_game.players["Harry"].possible_scores) == 2
    assert len(sample_game.players["Harry"].decisions) == 2
    assert sample_game.players["Harry"].bank_scores() == (100, [5, 5])
