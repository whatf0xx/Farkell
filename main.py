import game

if __name__ == "__main__":
    sample_roll = game.Roll(6, [4, 4, 4, 4, 1, 5])
    print(sample_roll)
    print(sample_roll.score())
