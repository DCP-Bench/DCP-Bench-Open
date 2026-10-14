# Age changing: find my age m and my husband's age h. Four operations (+2, /8, -3, *7)
# applied once each, in some order, take my age to his age. Applied in a different
# order, they take his age to mine.
from pyscipopt import Model, quicksum

# the four operations, by position in OPS
OPS = ["+2", "/8", "-3", "*7"]
# bounds on ages (years), and on intermediate results of the operations
MAX_AGE = 150
MAX_STATE = 2000
# number of operations applied in each sequence
STEPS = 4


def add_sequence(model, states, sel, tag):
    """Chain states[0] -> states[STEPS] through the operations selected by sel[p, o]."""
    # each position applies exactly one operation, and each operation is applied once
    for p in range(STEPS):
        model.addCons(quicksum(sel[p, o] for o in range(len(OPS))) == 1, name=f"{tag}_pos{p}")
    for o in range(len(OPS)):
        model.addCons(quicksum(sel[p, o] for p in range(STEPS)) == 1, name=f"{tag}_op{o}")

    for p in range(STEPS):
        x = states[p]
        z = states[p + 1]
        # +2: the result is the age plus 2
        model.addConsIndicator(z - x <= 2, binvar=sel[p, 0], name=f"{tag}_add2_le_{p}")
        model.addConsIndicator(z - x >= 2, binvar=sel[p, 0], name=f"{tag}_add2_ge_{p}")
        # /8: the age is divided by 8 exactly, so 8 times the result equals the age
        model.addConsIndicator(8 * z - x <= 0, binvar=sel[p, 1], name=f"{tag}_div8_le_{p}")
        model.addConsIndicator(8 * z - x >= 0, binvar=sel[p, 1], name=f"{tag}_div8_ge_{p}")
        # -3: the result is the age minus 3 (non-negative, through the domain of z)
        model.addConsIndicator(z - x <= -3, binvar=sel[p, 2], name=f"{tag}_sub3_le_{p}")
        model.addConsIndicator(z - x >= -3, binvar=sel[p, 2], name=f"{tag}_sub3_ge_{p}")
        # *7: the result is seven times the age
        model.addConsIndicator(z - 7 * x <= 0, binvar=sel[p, 3], name=f"{tag}_mul7_le_{p}")
        model.addConsIndicator(z - 7 * x >= 0, binvar=sel[p, 3], name=f"{tag}_mul7_ge_{p}")


def build(instance):
    model = Model()

    # my age m and my husband's age h, in years
    m = model.addVar(name="m", vtype="I", lb=0, ub=MAX_AGE)
    h = model.addVar(name="h", vtype="I", lb=0, ub=MAX_AGE)

    # first sequence: start from my age m and end at his age h
    a = [m] + [model.addVar(name=f"a{p}", vtype="I", lb=0, ub=MAX_STATE)
               for p in range(1, STEPS)] + [h]
    # second sequence: start from his age h and end at my age m
    b = [h] + [model.addVar(name=f"b{p}", vtype="I", lb=0, ub=MAX_STATE)
               for p in range(1, STEPS)] + [m]

    # sel1[p, o] = 1 if operation o is the one applied at position p of the first sequence
    sel1 = {(p, o): model.addVar(name=f"s1_{p}_{o}", vtype="B")
            for p in range(STEPS) for o in range(len(OPS))}
    # sel2[p, o] = 1 if operation o is the one applied at position p of the second sequence
    sel2 = {(p, o): model.addVar(name=f"s2_{p}_{o}", vtype="B")
            for p in range(STEPS) for o in range(len(OPS))}

    # the first sequence turns my age into his age, using each operation once
    add_sequence(model, a, sel1, "fwd")
    # the second sequence turns his age into mine, using each operation once
    add_sequence(model, b, sel2, "bwd")

    # the second sequence is in a different order: the two sequences do not
    # apply the same operation at every position
    same = {}
    for p in range(STEPS):
        for o in range(len(OPS)):
            same[p, o] = model.addVar(name=f"same_{p}_{o}", vtype="B")
            model.addConsAnd([sel1[p, o], sel2[p, o]], same[p, o])
    model.addCons(quicksum(same.values()) <= STEPS - 1, name="different_order")

    # outputs: my age m and my husband's age h (satisfaction problem, no objective)
    return model, {"h": h, "m": m}
