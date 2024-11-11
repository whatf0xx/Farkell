"""
Calculate the score for a given hand in Farkell. Should take as input the hand
as a list of ints between 1 and 6 (inclusive, obviously) and return a list of tuples of
the score as an int, and the dice that score as another list of ints. This is wrapped up
into a named tuple called a Score. Also provides functions for naming a hand or a score.
"""

from typing import NamedTuple


class Score(NamedTuple):
    """Score of a set of dice in Farkell, consists of the value of the score and the dice that compose it."""
    value: int
    dice: list[int]


class Combo6(NamedTuple):
    """Score and name for a combo of 6 dice in Farkell."""
    name: str
    score: int


def count(dice: list[int]) -> dict[int: int]:
    """
    Generate a dictionary of the number of occurrences of each dice.

    :param dice: the dice, given as a list of ints, where each element is a die.
    :return: dictionary mapping the dice value to the number of times it appears in the roll.
    """
    return {i: dice.count(i) for i in range(1, 7)}


def combo_of_6(counts: list[int]) -> Combo6:
    """Calculate scores for combinations of 6 dice."""
    if counts.count(1) == 6:
        return Combo6("ONE-TO-SIX STRAIGHT", 1500)
    elif counts.count(3) == 2:
        return Combo6("TWO TRIPLES", 2500)
    elif counts.count(2) == 3 or (counts.count(4) == 1 and counts.count(2) == 1):
        """For clarification, a 4-of-a-kind with a double counts as a 3-pair."""
        return Combo6("THREE PAIRS", 1500)
    elif counts.count(6) == 1:
        return Combo6("SIX OF A KIND", 3000)
    else:
        return Combo6("", 0)


def score_misc(dice: list[int]) -> list[Score]:
    """
    Score a hand of dice which has no combinations, i.e. it has only single or double 1s and 5s.

    :param dice: the hand of dice to score
    :return: the score breakdown. Each list element is a scoring part of the hand (these are always unique
             and don't overlap): first the score, and then the dice that contribute to that score.
    """
    score = []
    for die in dice:
        if die == 1:
            score.append(Score(100, [1]))
        elif die == 5:
            score.append(Score(50, [5]))

    return score


def score_combos(dice: list[int]) -> Score:
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
                    return Score(300, [1, 1, 1])
                return Score(i * 100, [i, i, i])
            case 4:
                return Score(1000, [i] * 4)
            case 5:
                return Score(2000, [i] * 5)
            case _:
                pass

    return Score(0, [])


def score_hand(dice: list[int]) -> list[Score]:
    no_dice = len(dice)
    if no_dice == 6:
        combo_6 = combo_of_6(list(count(dice).values()))
        if combo_6.name:
            return [Score(combo_6.score, dice)]  # if we have a combo of 6, we're done

    scores = []
    combos = score_combos(dice)
    if combos.dice:  # check that a combo was scored, else this is empty
        scores.append(combos)
        remaining_dice = [d for d in dice if d not in combos.dice]
    else:
        remaining_dice = dice

    misc = score_misc(remaining_dice)
    if misc:
        scores += misc

    scores.sort()
    """N.B. scoring tuples are SORTED, based on the score of the combo."""
    return scores


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
        case _: raise ValueError(f"unexpected number of ones ({ones}) and fives ({fives}) in miscellaneous hand.")


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


def name_hand(dice: list[int]) -> str:
    score_str = ""
    no_dice = len(dice)
    if no_dice == 6:
        combo_6 = combo_of_6(list(count(dice).values())).name
        if combo_6:
            return combo_6

    combo_name = name_combo(dice)
    combos = score_combos(dice)
    if combo_name:
        score_str += combo_name
        remaining_dice = [d for d in dice if d not in combos.dice]
    else:
        remaining_dice = dice

    misc = name_misc(remaining_dice)

    if score_str and misc:
        score_str += " AND " + misc
    elif misc:
        score_str = misc

    if not score_str:
        return "NO SCORE"
    return score_str
