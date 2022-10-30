import game

if __name__ == "__main__":
    # sample_roll = game.Roll(game.InputType.USER)
    # print(sample_roll.name_score())

    # sample_roll = game.Roll(6, [2, 3, 4, 6, 6, 2])
    # print(sample_roll)
    # print(sample_roll.score_total())
    # print(sample_roll.score_breakdown())

    # sample_turn = game.Turn()
    # sample_turn.bank_scores()
    # print(sample_turn.bank, sample_turn.no_dice)
    # sample_turn.reroll()
    # print(sample_turn)

    sample_game = game.Game()
    print(sample_game.dice_input)
    sample_game.play()

    # roll = game.Roll(game.InputType.USER, 6, [1, 2, 3, 4, 5, 6])
    # print(roll)
    # roll.roll([2, 3, 4, 3, 2, 2])
    # print(roll.score_breakdown())
    # print(game.bank_scores(roll.score_breakdown()))
