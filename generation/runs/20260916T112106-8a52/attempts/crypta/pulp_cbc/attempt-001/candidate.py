import pulp


def build(instance):
    """Crypta: a twenty-letter cryptarithmetic addition over ten distinct
    digits, checked seven digits at a time with two carries between blocks.
    """
    del instance

    names = "ABCDEFGHIJ"
    n = 10
    problem = pulp.LpProblem("crypta", pulp.LpMinimize)

    # All-different over the ten digits as a permutation matrix.
    pick = pulp.LpVariable.dicts("pick", (range(n), range(n)), cat="Binary")
    letter = {}
    for i, name in enumerate(names):
        letter[name] = pulp.LpVariable(name, 0, 9, cat="Integer")
        problem += pulp.lpSum(pick[i][d] for d in range(n)) == 1
        problem += letter[name] == pulp.lpSum(d * pick[i][d] for d in range(n))
    for d in range(n):
        problem += pulp.lpSum(pick[i][d] for i in range(n)) == 1

    a, b, c, d_, e, f, g, h, i_, j = (letter[x] for x in names)
    carry1 = pulp.LpVariable("carry1", cat="Binary")
    carry2 = pulp.LpVariable("carry2", cat="Binary")

    # No number may start with a zero.
    problem += b >= 1
    problem += d_ >= 1
    problem += g >= 1

    problem += (a + 10 * e + 100 * j + 1000 * b + 10000 * b + 100000 * e
                + 1000000 * f + e + 10 * j + 100 * e + 1000 * f + 10000 * g
                + 100000 * a + 1000000 * f
                == f + 10 * e + 100 * e + 1000 * h + 10000 * i_ + 100000 * f
                + 1000000 * b + 10000000 * carry1)
    problem += (c + 10 * f + 100 * h + 1000 * a + 10000 * i_ + 100000 * i_
                + 1000000 * j + f + 10 * i_ + 100 * b + 1000 * d_ + 10000 * i_
                + 100000 * d_ + 1000000 * c + carry1
                == j + 10 * f + 100 * a + 1000 * f + 10000 * h + 100000 * d_
                + 1000000 * d_ + 10000000 * carry2)
    problem += (a + 10 * j + 100 * j + 1000 * i_ + 10000 * a + 100000 * b + b
                + 10 * a + 100 * g + 1000 * f + 10000 * h + 100000 * d_ + carry2
                == c + 10 * a + 100 * g + 1000 * e + 10000 * j + 100000 * g)

    return problem, {name: letter[name] for name in names}
