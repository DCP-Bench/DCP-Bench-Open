"""Ages of the sons: the product of the three sons' ages is 36, their sum alone does not
determine them (another triple with product 36 has the same sum), and there is a single
oldest son. What are the ages?

The model reports the ages A1, A2, A3, oldest first.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its constants are below

    product = 36  # the product of the ages, from the puzzle statement
    top = 36  # ages range over 0..36, as in the reference

    problem = pulp.LpProblem("ages_of_the_sons", pulp.LpMinimize)  # satisfaction

    # A product of variables is not linear, so each triple of ages is chosen from the
    # table of non-increasing triples in 0..top whose product is 36.
    triples = [(a, b, c) for a in range(top + 1) for b in range(a + 1) for c in range(b + 1)
               if a * b * c == product]

    def chosen_triple(name):
        pick = {t: pulp.LpVariable(f"{name}_{t[0]}_{t[1]}_{t[2]}", cat="Binary")
                for t in triples}
        problem += pulp.lpSum(pick.values()) == 1
        ages = [pulp.lpSum(t[k] * var for t, var in pick.items()) for k in range(3)]
        return pick, ages

    # A1 >= A2 >= A3 are the sons' ages and their product is 36
    pick_a, (a1, a2, a3) = chosen_triple("A")
    # B1 >= B2 >= B3 is another triple of ages with product 36
    pick_b, (b1, b2, b3) = chosen_triple("B")

    A1 = pulp.LpVariable("A1", 0, top, cat="Integer")
    A2 = pulp.LpVariable("A2", 0, top, cat="Integer")
    A3 = pulp.LpVariable("A3", 0, top, cat="Integer")
    problem += A1 == a1
    problem += A2 == a2
    problem += A3 == a3

    # the oldest son is unique: A1 > A2
    problem += A1 >= A2 + 1

    # the other triple has a different oldest age, so it is a different triple
    # (A1 != B1 as one of two strict inequalities, chosen by a binary)
    b_older = pulp.LpVariable("b_older", cat="Binary")
    problem += A1 <= b1 - 1 + (top + 1) * (1 - b_older)
    problem += A1 >= b1 + 1 - (top + 1) * b_older

    # both triples have the same sum: the number of windows did not decide it
    problem += A1 + A2 + A3 == b1 + b2 + b3

    return problem, {"A1": A1, "A2": A2, "A3": A3}
