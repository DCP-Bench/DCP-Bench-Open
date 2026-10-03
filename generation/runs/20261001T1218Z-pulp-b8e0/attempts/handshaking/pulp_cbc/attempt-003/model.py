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
    ranks = range(n - 1)  # the possible numbers of hands of a person: 0..n-2

    problem = pulp.LpProblem("handshaking", pulp.LpMinimize)  # satisfaction: no objective

    # A person shakes hands with nobody but others and not with the spouse, so nobody shakes
    # more than n - 2 hands. The people other than Hilary are n - 1 and all have a different
    # number of hands, so each number 0..n-2 is the number of hands of exactly one of them.
    # The handshakes are described by those numbers instead of by the people: "the person with r
    # hands" is a single person for every r. has[i][r] = 1 if person i (not Hilary) has shaken r
    # hands, so every person has one number and every number belongs to one person.
    has = pulp.LpVariable.dicts("has", (range(1, n), ranks), cat="Binary")
    for i in range(1, n):
        problem += pulp.lpSum(has[i][r] for r in ranks) == 1
    for r in ranks:
        problem += pulp.lpSum(has[i][r] for i in range(1, n)) == 1

    # shake[(r, s)] = 1 if the person with r hands and the person with s hands shake hands
    # (r < s); handshaking is symmetric, so one variable stands for both directions. Nobody
    # shakes hands with themselves.
    shake = {(r, s): pulp.LpVariable(f"shake_{r}_{s}", cat="Binary")
             for r in ranks for s in ranks if r < s}

    def together(r, s):
        """the variable for the handshake of the people with r and s hands (r != s)"""
        return shake[(min(r, s), max(r, s))]

    # shake_hil[r] = 1 if Hilary shakes hands with the person who has r hands
    shake_hil = [pulp.LpVariable(f"shake_hil_{r}", cat="Binary") for r in ranks]

    # The person with r hands has shaken exactly r hands, with other people or with Hilary.
    for r in ranks:
        problem += pulp.lpSum(together(r, s) for s in ranks if s != r) + shake_hil[r] == r

    # Nobody shakes hands with their spouse. For a couple (2k, 2k + 1), if one has r hands and
    # the other s hands, the people with r and s hands do not shake hands.
    for k in range(1, num_couples + 1):
        for r in ranks:
            for s in ranks:
                if r != s:
                    problem += together(r, s) + has[2 * k][r] + has[2 * k + 1][s] <= 2

    # Hilary does not shake hands with her spouse Jocelyn, person 1
    for r in ranks:
        problem += shake_hil[r] + has[1][r] <= 1

    # hil = the number of hands Hilary has shaken (the number of people she shook hands with);
    # at most n - 2 since she has no handshake with herself or with Jocelyn
    hil = pulp.LpVariable("hil", 0, n - 2, cat="Integer")
    problem += hil == pulp.lpSum(shake_hil)

    return problem, {"hil": hil}
