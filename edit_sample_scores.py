import pickle

with open("rolls-scores.pkl", "rb") as file:
    rolls = pickle.load(file)

rolls[(6, 1, 5, 2, 6, 2)] = 150

with open("rolls-scores.pkl", "wb") as file:
    pickle.dump(rolls, file)