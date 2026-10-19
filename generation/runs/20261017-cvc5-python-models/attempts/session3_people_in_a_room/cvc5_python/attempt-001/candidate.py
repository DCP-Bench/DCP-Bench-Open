# Problem: session3_people_in_a_room
# 13 people enter a room one at a time; 4 of them are male. Find an entry order such that
# the ratio of females to males in the room at any one time is no greater than 7/3.
# Output "sequence": [13]bool, 0 = male, 1 = female (here seq[i] is True when entrant i is female).

import cvc5.pythonic as cz


def build(instance):
    n_people = 13
    n_males = 4
    n_females = n_people - n_males
    seq = [cz.Bool(f"female_{i}") for i in range(n_people)]

    constraints = []

    # There are 13 people. 4 of them are male.
    constraints.append(cz.Sum([cz.If(b, 1, 0) for b in seq]) == n_females)

    # They randomly enter a room one at a time. Find a way that the males and females enter so that
    # the ratio of females to males in the room at any one time is no greater than 7/3.
    # After the t-th entrant, with f females and m = t - f males in the room: f / m <= 7/3,
    # i.e. 3 * f <= 7 * m, which is 10 * f <= 7 * t.
    for t in range(1, n_people + 1):
        females_in_room = cz.Sum([cz.If(seq[i], 1, 0) for i in range(t)])
        constraints.append(10 * females_in_room <= 7 * t)

    return constraints, {"sequence": seq}
