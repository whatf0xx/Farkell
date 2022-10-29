import game

def test_game_turn():
    sample_game = game.Game(game.InputType.COM, game.InputType.COM, {"Harry": game.InputType.USER}, 10000, 500)
    sample_game.players["Harry"].set_strategy("LAZY-BANK")
    sample_game.players["Harry"].set_possible_scores([[50, [5]], [50, [5]]])
    assert sample_game.players["Harry"].bank_scores() == (100, [5, 5])  # given that the user input is to bank the score
