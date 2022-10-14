from itertools import product, cycle
from random import randint
import pickle

exists = True
no_samples = 50

if exists:
    with open("rolls-scores.pkl", "rb") as file:
        rolls = pickle.load(file)
else:
    rolls = {}

i, prev_roll = 0, 0

for roll in cycle(product(range(1, 7), repeat=6)):
    r = randint(1, 4993)
    if r == 1:
        rolls[roll] = int(input(sorted(roll)))
        if rolls[roll] == -1:
            del rolls[roll]
            del rolls[prev_roll]
            break

        prev_roll = roll
        i += 1

    if i == no_samples:
        break

with open("rolls-scores.pkl", 'wb') as file:
    pickle.dump(rolls, file)
