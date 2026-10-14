# Five brigands: find the doubloons A, B, C, D, E of five brigands, with each at least one, that total 200 and still total 200 after the multipliers 12, 3, 1, 1/2, 1/3.
from pyscipopt import Model, quicksum


def build(instance):
    m = Model()

    # the doubloons of Alfonso, Benito, Carlos, Diego and Esteban; each has at least one doubloon
    # the total of the five is 200, so no brigand can have more than 200 - 4 = 196
    A = m.addVar(name="A", vtype="I", lb=1, ub=196)
    B = m.addVar(name="B", vtype="I", lb=1, ub=196)
    C = m.addVar(name="C", vtype="I", lb=1, ub=196)
    D = m.addVar(name="D", vtype="I", lb=1, ub=196)
    E = m.addVar(name="E", vtype="I", lb=1, ub=196)

    # they had altogether exactly 200 doubloons
    m.addCons(A + B + C + D + E == 200)

    # with Alfonso at twelve times, Benito at three times, Carlos the same, Diego half and Esteban one-third, the total is still 200
    # multiplied by 6 to keep the coefficients integral: 72A + 18B + 6C + 3D + 2E = 1200
    m.addCons(72 * A + 18 * B + 6 * C + 3 * D + 2 * E == 1200)

    # the output gives the doubloons of A, B, C, D, E
    return m, {"A": A, "B": B, "C": C, "D": D, "E": E}
