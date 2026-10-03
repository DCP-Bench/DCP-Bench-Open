"""Handshaking: Hilary and Jocelyn are married and invite some couples to dinner. Everybody
shakes hands with some of the others, nobody with themselves or with their own spouse, and
all the people except Hilary have shaken a different number of hands. How many hands has
Hilary shaken?

The model reports the number of hands Hilary has shaken.
"""
import pulp


def build(instance):
    num_couples = instance["num_couples"]  # invited couples, not counting Hilary and Jocelyn
    n = 2 + num_couples * 2  # number of people; person 2k and 2k + 1 are a couple
    # Person 0 is Hilary and person 1 is her spouse Jocelyn (the same coding as the reference).

    problem = pulp.LpProblem("handshaking", pulp.LpMinimize)  # satisfaction: no objective

    # shake[(i, j)] = 1 if persons i and j shake hands (i < j). Handshaking is symmetric,
    # so one variable stands for both directions. Nobody shakes hands with themselves (no
    # variable for i == i) or with their spouse (no variable for the pair 2k, 2k + 1).
    shake = {}
    for i in range(n):
        for j in range(i + 1, n):
            if not (i % 2 == 0 and j == i + 1):
                shake[(i, j)] = pulp.LpVariable(f"shake_{i}_{j}", cat="Binary")

    def hands_of(i):
        """the handshakes person i takes part in"""
        return [shake[(min(i, j), max(i, j))] for j in range(n)
                if j != i and (min(i, j), max(i, j)) in shake]

    # x[i] = number of hands person i has shaken; nobody can shake more than n - 2 hands
    # (not themselves, not their spouse)
    x = [pulp.LpVariable(f"x_{i}", 0, n - 2, cat="Integer") for i in range(n)]
    for i in range(n):
        problem += x[i] == pulp.lpSum(hands_of(i))

    # Every handshake is counted by both of its two people, so the counts add up to twice
    # the number of handshakes. This follows from the definitions above but CBC cannot
    # derive that the total is even, so it is stated with an integer for the number of
    # handshakes.
    pairs = pulp.LpVariable("handshakes", 0, len(shake), cat="Integer")
    problem += pulp.lpSum(x) == 2 * pairs

    # All the people except Hilary have shaken a different number of hands. That is n - 1
    # people and the n - 1 counts 0..n-2, so all-different is an assignment matrix:
    # count[i][v] = 1 if person i has shaken v hands.
    count = pulp.LpVariable.dicts("count", (range(1, n), range(n - 1)), cat="Binary")
    for i in range(1, n):
        problem += pulp.lpSum(count[i][v] for v in range(n - 1)) == 1
        problem += x[i] == pulp.lpSum(v * count[i][v] for v in range(n - 1))
    for v in range(n - 1):
        problem += pulp.lpSum(count[i][v] for i in range(1, n)) == 1

    return problem, {"hil": x[0]}
