# Handshaking (Halmos): Hilary and Jocelyn are married and invite n couples; nobody shakes hands with self or spouse, and the hand counts Jocelyn asks for are all different.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["num_couples"]
    # Persons 2k and 2k+1 form couple k. Couple 0 is Hilary (0) and Jocelyn (1).
    people = list(range(2 * (n + 1)))
    hilary, jocelyn = 0, 1
    top = len(people) - 2  # a person can shake hands with everyone except self and spouse

    m = Model()

    # shake[p, q] = 1 if p and q shook hands (p < q, not spouses)
    shake = {
        (p, q): m.addVar(name=f"shake_{p}_{q}", vtype="B")
        for p in people
        for q in people
        if p < q and q != (p ^ 1)
    }

    def pair(p, q):
        return shake[min(p, q), max(p, q)]

    def hands(p):
        # number of hands person p has shaken
        return quicksum(pair(p, q) for q in people if q != p and q != (p ^ 1))

    # hand-count value of each person, one-hot encoded
    code = {
        (p, v): m.addVar(name=f"hands_{p}_is_{v}", vtype="B")
        for p in people
        for v in range(top + 1)
    }
    for p in people:
        # each person has exactly one number of hands shaken
        m.addCons(quicksum(code[p, v] for v in range(top + 1)) == 1)
        m.addCons(hands(p) == quicksum(v * code[p, v] for v in range(top + 1)))

    # all the answers are different: each number of hands is given by exactly one guest Jocelyn asks
    # (2n+1 guests and 2n+1 possible answers 0..2n, so every value occurs once)
    for v in range(top + 1):
        m.addCons(quicksum(code[p, v] for p in people if p != jocelyn) == 1)

    # the answers run from 0 to 2n, so each invited couple's two answers add up to 2n
    # (the guest with the most hands shook everyone but the spouse, the guest with none shook nobody)
    for k in range(1, n + 1):
        m.addCons(hands(2 * k) + hands(2 * k + 1) == 2 * n)

    # symmetry breaking: couples 1..n can be permuted freely, so order the husbands by their answers
    # (the answers are all different, so the order is strict)
    for k in range(1, n):
        m.addCons(hands(2 * k) >= hands(2 * k + 2) + 1)

    return m, {"hil": hands(hilary)}
