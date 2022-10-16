import game

if __name__ == "__main__":
    # sample_roll = game.Roll()
    sample_roll = game.Roll(6, [2, 3, 4, 6, 6, 2])
    print(sample_roll)
    print(sample_roll.score())

    sample_hand = game.Hand(sample_roll, 0)
    print(sample_hand.get_score())
