"""Finding celebrities at a party.

A party has n people; graph[j][i] = 1 when person j knows person i (the diagonal
is the person knowing him or herself). A celebrity is a person whom everybody at
the party knows, but who only knows other celebrities. At least one celebrity is
present. Output: celebrities[i] = 1 when person i is a celebrity.

Encoding: one Bool per person, c_i = "person i is a celebrity". Each person's
condition is written out as one constraint block; the knowledge data comes
from the instance graph.
"""

from paramita.modelling import And, Bool, Iff, Or


def build(instance):
    g = instance["graph"]
    n = len(g)
    c = [Bool(f"celebrity_{i}") for i in range(n)]
    cons = []

    for i in range(n):
        # everybody at the party knows person i (the diagonal counts: i knows i)
        known_by_all = all(g[j][i] == 1 for j in range(n))
        # the people that i knows, other than i
        others = [j for j in range(n) if j != i and g[i][j] == 1]

        # a celebrity is known by everybody; if someone does not know i, i is not a celebrity
        if not known_by_all:
            cons.append(~c[i])
            continue

        # a celebrity only knows other celebrities: i is a celebrity exactly when
        # every person that i knows (other than i) is a celebrity
        if not others:
            cons.append(c[i])
        elif len(others) == 1:
            cons.append(Iff(c[i], c[others[0]]))
        else:
            cons.append(Iff(c[i], And([c[j] for j in others])))

    # at least one celebrity is present at the party
    cons.append(Or(c))

    return cons, {"celebrities": c}
