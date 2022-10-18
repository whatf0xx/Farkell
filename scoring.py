"""
Calculate the score for a given hand in Farkell. Should take as input the hand
as a list of ints between 1 and 6 (inclusive, obviously) and return a list of tuples of
the score as an int, and the dice that score as another list of ints.
"""


def count(dice: list[int]) -> dict[int: int]:
    """
    Generate a dictionary of the number of occurrences of each dice.

    :param dice: the dice, given as a list of ints, where each element is a die.
    :return: dictionary mapping the dice value to the number of times it appears in the roll.
    """
    return {i: dice.count(i) for i in range(1, 7)}


def score_misc(dice: list[int]) -> list[tuple[int, list[int]]]:
    """
    Score a hand of dice which has no combinations, i.e. it has only single or double 1s and 5s.

    :param dice: the hand of dice to score
    :return: the score breakdown. Each list element is a scoring part of the hand (these are always unique
             and don't overlap): first the score, and then the dice that contribute to that score.
    """
    score = []
    for die in dice:
        if die == 1:
            score.append((100, [1]))
        elif die == 5:
            score.append((50, [5]))

    return score


def score_combos(dice: list[int]) -> tuple[int, list[int]]:
    """
    Score the combos in a hand of dice, excluding the 6-dice combos, i.e. the provided roll does not have
    2 triples, a straight, 6 of a kind etc.

    :param dice: the hand of dice to score
    :return: the score breakdown. As only one combo per roll is possible, only the tuple of the score with
             the associated dice is returned.
    """
    counts = count(dice)
    for i in counts:
        match counts[i]:
            case 3:
                if i == 1:
                    return 300, [1, 1, 1]
                return i * 100, [i, i, i]
            case 4:
                return 1000, [i] * 4
            case 5:
                return 2000, [i] * 5
            case _:
                pass

    return 0, []


def name_misc(dice: list[int]) -> str:
    """
    Name the misc (i.e. non-combo scoring) dice in the hand. There can be at most 2 of any die.

    :param dice: the hand of dice to name
    :return: string representation of the name of the hand
    """
    ones = dice.count(1)
    fives = dice.count(5)

    match (ones, fives):
        case 0, 0: return ""
        case 1, 0: return "A MOOSE"
        case 0, 1: return "A FIVE"
        case 1, 1: return "A MOOSE AND A FIVE"
        case 2, 0: return "TWO MOOSE"
        case 2, 1: return "TWO MOOSE AND A FIVE"
        case 0, 2: return "TWO FIVES"
        case 1, 2: return "A MOOSE AND TWO FIVES"
        case 2, 2: return "TWO MOOSE AND TWO FIVES"
        case _: raise ValueError(f"unexpected number of ones {ones} and fives {fives} in miscellaneous hand.")


def name_combo(dice: list[int]) -> str:
    """
    Name the combo of dice (excluding 6-dice combos) scoring in the hand.

    :param dice: the hand of dice to name
    :return: string representation of the name of the hand
    """
    counts = count(dice)
    for i in counts:
        match counts[i]:
            case 3: return "THREE OF A KIND"
            case 4: return "FOUR OF A KIND"
            case 5: return "FIVE OF A KIND"
            case 6: raise ValueError("6 OF A KIND roll passed.")
            case _: pass

    return ""


def combo_of_6(counts: list[int]) -> tuple[str, int]:
    """Calculate scores for combinations of 6 dice."""
    if counts.count(1) == 6:
        return "ONE-TO-SIX STRAIGHT", 1500
    elif counts.count(3) == 2:
        return "TWO TRIPLES", 2500
    elif counts.count(2) == 3 or (counts.count(4) == 1 and counts.count(2) == 1):
        """For clarification, a 4-of-a-kind with a double counts as a 3-pair."""
        return "THREE PAIRS", 1500
    elif counts.count(6) == 1:
        return "SIX OF A KIND", 3000
    else:
        return "", 0
