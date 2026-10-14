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
    # the number of handshakes. This follows from the definitions above; it is stated with an
    # integer for the number of handshakes so that the solver sees the total is even.
    pairs = pulp.LpVariable("handshakes", 0, len(shake), cat="Integer")
    problem += pulp.lpSum(x) == 2 * pairs

    # count[i][v] = 1 if person i has shaken v hands. All the people except Hilary have shaken a
    # different number of hands: that is n - 1 people and the n - 1 counts 0..n-2, so each
    # count 0..n-2 is shaken by exactly one of them. Hilary's count is not restricted.
    count = pulp.LpVariable.dicts("count", (range(n), range(n - 1)), cat="Binary")
    for i in range(n):
        problem += pulp.lpSum(count[i][v] for v in range(n - 1)) == 1
        problem += x[i] == pulp.lpSum(v * count[i][v] for v in range(n - 1))
    for v in range(n - 1):
        problem += pulp.lpSum(count[i][v] for i in range(1, n)) == 1

    # Redundant bounds on the hands, true in every solution: they add no restriction but give
    # the solver a tighter linear picture of which counts can be realised by handshakes.
    # Take the k people (not Hilary) who shook the most hands, that is those with a count of
    # n - 1 - k or more. A hand they shook goes to somebody in the group (at most k * (k - 1)
    # hands, since each of the k people has at most k - 1 partners in the group) or to somebody
    # outside it, who shakes at most min(count, k) hands with the group.
    def group_hands(k):
        """total hands of the k people (not Hilary) with the highest counts"""
        return pulp.lpSum(v * count[i][v] for i in range(1, n) for v in range(n - 1 - k, n - 1))

    def outside_hands(k, size, hilary_outside):
        """hands that the people outside a group of the given size can have with the group: each
        of them at most min(count, size). Outside are the people (not Hilary) with a count below
        n - 1 - k, and Hilary, with any count, when she is not in the group"""
        outside = pulp.lpSum(min(v, size) * count[i][v]
                             for i in range(1, n) for v in range(n - 1 - k))
        if hilary_outside:
            outside += pulp.lpSum(min(v, size) * count[0][v] for v in range(n - 1))
        return outside

    for k in range(1, n - 1):
        # the group of the k highest counts, Hilary outside it
        problem += group_hands(k) <= k * (k - 1) + outside_hands(k, k, True)
    for k in range(0, n - 1):
        # the same group with Hilary added to it (k + 1 people), Hilary's own hands included
        problem += group_hands(k) + x[0] <= (k + 1) * k + outside_hands(k, k + 1, False)

    return problem, {"hil": x[0]}
