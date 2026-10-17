# Exodus (session3_exodus): five children at Hebrew school (Bernice, Carl, Debby,
# Sammy, Ted) each present one part of the Exodus story. Each child has a different
# age (three, five, seven, eight or ten), and each family came from a different
# country (Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen). Find the age, the country
# and the story of each child.
#
# Encoding: five houses (1..5) tie the four categories together. Each category has a
# permutation matrix X[cat][entity][house]; an output value is the house number of its
# entity, so the same number links the four output lists. Pairs of entities that share
# a house are linked by binaries S, which feed the age relations as linear expressions.
import mip

# constants fixed by the problem statement (not by the instance)
AGES = [3, 5, 7, 8, 10]  # ages in the order of the statement
CHILD = {"Bernice": 0, "Carl": 1, "Debby": 2, "Sammy": 3, "Ted": 4}
COUNTRY = {"Ethiopia": 0, "Kazakhstan": 1, "Lithuania": 2, "Morocco": 3, "Yemen": 4}
STORY = {"burning bush": 0, "captivity": 1, "Moses": 2, "Passover": 3, "Ten Commandments": 4}

# ages lie in 3..10, so any difference of two ages is at most 7 in absolute value;
# M = 20 covers that together with the offsets 1, 2 and 3 used below
M = 20


def build(instance):
    n = 5
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # one house per entity and one entity per house, for each of the four categories
    cats = ["age", "child", "country", "story"]
    X = {}
    for cat in cats:
        X[cat] = [[model.add_var(f"{cat}_{e}_{h}", var_type=mip.BINARY) for h in range(n)]
                  for e in range(n)]
        for e in range(n):
            model.add_constr(mip.xsum(X[cat][e]) == 1)
        for h in range(n):
            model.add_constr(mip.xsum(X[cat][e][h] for e in range(n)) == 1)

    def same_house(cat1, e1, cat2, e2):
        # s = 1 exactly when entity e1 of cat1 and entity e2 of cat2 are in the same house
        s = model.add_var(f"same_{cat1}{e1}_{cat2}{e2}", var_type=mip.BINARY)
        for h in range(n):
            a = X[cat1][e1][h]
            b = X[cat2][e2][h]
            model.add_constr(s >= a + b - 1)
            model.add_constr(s <= 1 - a + b)
            model.add_constr(s <= 1 + a - b)
        return s

    # S_age[c][a], S_country[c][k], S_story[c][s]: child c has age a, country k, story s
    S_age = [[same_house("child", c, "age", a) for a in range(n)] for c in range(n)]
    S_country = [[same_house("child", c, "country", k) for k in range(n)] for c in range(n)]
    S_story = [[same_house("child", c, "story", s) for s in range(n)] for c in range(n)]

    def age(c):
        return mip.xsum(AGES[a] * S_age[c][a] for a in range(n))

    def implies_difference(flag, expr, rhs):
        # flag = 1 implies expr == rhs (expr is linear, bounded by M)
        model.add_constr(expr - rhs <= M * (1 - flag))
        model.add_constr(expr - rhs >= -M * (1 - flag))

    # Debby's family is from Lithuania.
    model.add_constr(S_country[CHILD["Debby"]][COUNTRY["Lithuania"]] == 1)

    # The child who told the story of the Passover is two years older than Bernice.
    b = CHILD["Bernice"]
    p = STORY["Passover"]
    for c in range(n):
        if c == b:
            model.add_constr(S_story[c][p] == 0)
        else:
            implies_difference(S_story[c][p], age(c) - age(b), 2)

    # The child whose family is from Yemen is younger than the child from the Ethiopian family.
    y = COUNTRY["Yemen"]
    et = COUNTRY["Ethiopia"]
    for c in range(n):
        for d in range(n):
            if c == d:
                continue
            both = S_country[c][y] + S_country[d][et]
            model.add_constr(age(c) - age(d) + 1 <= M * (2 - both))

    # The child from the Moroccan family is three years older than Ted.
    t = CHILD["Ted"]
    mo = COUNTRY["Morocco"]
    for c in range(n):
        if c == t:
            model.add_constr(S_country[c][mo] == 0)
        else:
            implies_difference(S_country[c][mo], age(c) - age(t), 3)

    # Sammy is three years older than the child who told the story of Moses's youth
    # in the house of the Pharaoh.
    sa = CHILD["Sammy"]
    mz = STORY["Moses"]
    for c in range(n):
        if c == sa:
            model.add_constr(S_story[c][mz] == 0)
        else:
            implies_difference(S_story[c][mz], age(sa) - age(c), 3)

    # Output: for each entity, the house number (1..5) it sits in.
    def house_number(cat, e):
        return mip.xsum((h + 1) * X[cat][e][h] for h in range(n))

    outputs = {
        "ages": [house_number("age", e) for e in range(n)],
        "children": [house_number("child", e) for e in range(n)],
        "countries": [house_number("country", e) for e in range(n)],
        "stories": [house_number("story", e) for e in range(n)],
    }
    return model, outputs
