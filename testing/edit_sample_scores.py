import pickle

with open("rolls-scores.pkl", "rb") as file:
    rolls = pickle.load(file)

# for roll in rolls:
#     combos = []
#     while True:
#         user_input = input((roll, rolls[roll]))
#         if not user_input:
#             break
#         if user_input == "0":
#             combos = [(0, [])]
#             break
#
#         input_list = [int(c) for c in user_input.split()]
#         combos.append((input_list[0], input_list[1:]))
#
#     rolls[roll] = (rolls[roll], combos)

# rolls[(5, 3, 4, 2, 3, 2)] = (rolls[(5, 3, 4, 2, 3, 2)][0], [(50, [5])])

with open("rolls-scores.pkl", "wb") as file:
    pickle.dump(rolls, file)
