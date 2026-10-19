# Circling the squares: place a different whole number in each of ten squares
# A, B, C, D, E, F, G, H, I, K arranged in a circle. Fractions are not allowed,
# and no number needs more than two figures, so each number is between 0 and 99.
# The four numbers A=16, B=2, F=8, G=14 are given and stay as they are.
import mip

NAMES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]
N = len(NAMES)
LO, HI = 0, 99
VALUES = list(range(LO, HI + 1))


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Each square takes one value: one-hot binaries p[i][v], x[i] is the value,
    # sq[i] is its square. Only linear rows are needed for the squares.
    p = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in VALUES]
         for i in range(N)]
    x = [model.add_var(NAMES[i], lb=LO, ub=HI, var_type=mip.INTEGER)
         for i in range(N)]
    sq = [model.add_var(f"sq_{i}", lb=0, ub=HI * HI, var_type=mip.INTEGER)
          for i in range(N)]

    for i in range(N):
        # each square holds exactly one number
        model.add_constr(mip.xsum(p[i][k] for k in range(len(VALUES))) == 1)
        model.add_constr(x[i] == mip.xsum(v * p[i][k] for k, v in enumerate(VALUES)))
        model.add_constr(sq[i] == mip.xsum(v * v * p[i][k] for k, v in enumerate(VALUES)))

    # a different number in each of the ten squares
    for k in range(len(VALUES)):
        model.add_constr(mip.xsum(p[i][k] for i in range(N)) <= 1)

    # the sum of the squares of any two adjacent numbers shall be equal to the
    # sum of the squares of the two numbers diametrically opposite to them
    for i in range(N):
        model.add_constr(
            sq[i] + sq[(i + 1) % N] == sq[(i + 5) % N] + sq[(i + 6) % N]
        )

    # the given numbers: A=16, B=2, F=8, G=14
    given = {"A": 16, "B": 2, "F": 8, "G": 14}
    for name, value in given.items():
        model.add_constr(x[NAMES.index(name)] == value)

    # satisfaction problem: no objective
    outputs = {name: x[i] for i, name in enumerate(NAMES)}
    return model, outputs
