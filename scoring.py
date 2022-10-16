"""
Calculate the score for a given hand in Farkell. Should take as input the hand
as a list of ints between 1 and 6 (inclusive, obviously) and return a list of tuples of
the score as an int, and the dice that score as another list of ints.
"""


def count(dice: list[int]) -> dict[int: int]:
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
    2 triples, a straight etc.

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
            case 6:
                return 3000, [i] * 6
            case _:
                pass

    return 0, []


def combo_of_6(counts: list[int]) -> tuple[str, int]:
    """Calculate scores for combinations of 6 dice."""
    if counts.count(1) == 6:
        return "1-6 STRAIGHT", 1500
    elif counts.count(3) == 2:
        return "2 TRIPLES", 2500
    elif counts.count(2) == 3 or (counts.count(4) == 1 and counts.count(2) == 1):
        """For clarification, a 4-of-a-kind with a double counts as a 3-pair."""
        return "3 PAIRS", 1500
    elif counts.count(6) == 1:
        return "6-OF-A-KIND", 3000
    else:
        return "", 0


def score_single(die: int) -> tuple[str, int]:
    """Get the score for a single die."""
    match die:
        case 1: return "A MOOSE", 100
        case 5: return "A 5", 50
        case _: return "", 0


def score_2(dice: list[int]) -> tuple[str, int]:
    """Get the score for 2 dice."""
    dice.sort()  # saves an extra check
    match dice:
        case [1, 1]:
            return "2 MOOSE", 200
        case [1, 5]:
            return "A MOOSE AND A 5", 150
        case [5, 5]:
            return "2 5S", 100
        case _:
            return "", 0


def score_3(counts: dict[int: int]) -> tuple[str, int]:
    for i in counts:
        if counts[i] == 3:
            if i == 1:
                return "3 MOOSE", 300
            else:
                return f"3 {i}S", i * 100

    score_tuples = []

    if 1 not in counts and 5 not in counts:
        return "", 0

    if 1 in counts:  # if there are moose
        match counts[1]:
            case 1: score_tuples.append(("A MOOSE", 100))
            case 2: score_tuples.append(("2 MOOSE", 200))
            case _: score_tuples.append(("", 0))

    if 5 in counts:
        match counts[5]:
            case 1: score_tuples.append(("A 5", 50))
            case 2: score_tuples.append(("2 5S", 100))
            case _: score_tuples.append(("", 0))

    return " AND ".join([s[0] for s in score_tuples if s[0]]), sum([s[1] for s in score_tuples])


def score_4(counts: dict[int: int]) -> tuple[str, int]:
    """Calculate the score for a roll of 4 dice."""
    score_tuples = []
    """First, check for a 4-of-a-kind"""
    if 4 in counts.values():
        return "4 OF A KIND", 1000

    """Check for 3-of-a-kind and a single"""
    if 3 in counts.values():
        score_tuples.append(score_3({i: counts[i] for i in counts if counts[i] == 3}))  # slow but easy
        single = [die for die in counts if counts[die] == 1][0]  # gets the value of the other die
        score_tuples.append(score_single(single))
        return " AND ".join([s[0] for s in score_tuples if s[0]]), sum([s[1] for s in score_tuples])

    """If we're here, then we must have 4 miscellaneous dice. We have no more than 2 of any face."""
    if counts[1] == 2 and counts[5] == 2:
        return "2 MOOSE AND 2 5s", 300

    """Then what remains is at most 3 scoring dice, we can just call score_3 on this"""
    return score_3(counts)


def score_5(counts: dict[int: int]) -> tuple[str, int]:
    """Calculate the score for a roll of 5 dice."""
    score_tuples = []
    if 5 in counts.values():
        return "5 OF A KIND", 2000

    if 4 in counts.values():
        score_tuples.append(("4-OF-A-KIND", 1000))
        single = [die for die in counts if counts[die] == 1][0]  # gets the value of the other die
        score_tuples.append(score_single(single))
        return " AND ".join([s[0] for s in score_tuples if s[0]]), sum([s[1] for s in score_tuples])

    if 3 in counts.values():
        score_tuples.append(score_3({i: counts[i] for i in counts if counts[i] == 3}))  # slow but easy
        double = [die for die in counts if counts[die] != 3]  # gets the value of the other die
        score_tuples.append(score_2(double))
        return " AND ".join([s[0] for s in score_tuples if s[0]]), sum([s[1] for s in score_tuples])

    """Then we have at most pairs, or single die."""
    return score_4(counts)  # this handles the given case


def score_6(counts: dict[int: int]) -> tuple[str, int]:
    """Calculate the score for a roll of 6 dice."""
    score_tuples = []
    """First, check if we hit a combo of 6."""
    combo_6_score = combo_of_6(list(counts.values()))
    if combo_6_score[0]:
        """If we got a combo of 6, we are done with the scoring."""
        return combo_6_score

    """Now we need to check if we have a 5-of-a-kind and a single."""
    if 5 in counts.values():
        score_tuples.append(("5-OF-A-KIND", 2000))
        single = [die for die in counts if counts[die] == 1][0]  # gets the value of the other die
        score_tuples.append(score_single(single))
        return " AND ".join([s[0] for s in score_tuples if s[0]]), sum([s[1] for s in score_tuples])

    """Next, 4-of-a-kind"""
    if 4 in counts.values():
        score_tuples.append(("4 OF A KIND", 1000))
        double = [die for die in counts if counts[die] == 1 or counts[die] == 2]
        score_tuples.append(score_2(double))
        return " AND ".join([s[0] for s in score_tuples if s[0]]), sum([s[1] for s in score_tuples])

    """3-of-a-kind, N.B. we can't have 2 different 3-of-a-kinds, that case was handles above."""
    if 3 in counts.values():
        score_tuples.append((score_3({i: counts[i] for i in counts if counts[i] == 3})))
        remaining = {i: counts[i] for i in counts if counts[i] != 3}
        score_tuples.append(score_3(remaining))
        return " AND ".join([s[0] for s in score_tuples if s[0]]), sum([s[1] for s in score_tuples])

    """Then we have at most 2 of any die, we can pass this to score_4"""
    return score_4(counts)
