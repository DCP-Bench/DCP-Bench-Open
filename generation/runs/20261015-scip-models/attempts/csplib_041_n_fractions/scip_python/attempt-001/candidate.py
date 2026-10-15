# Find distinct non-zero digits A..I with A/BC + D/EF + G/HI = 1, where BC, EF, HI are two-digit numbers.
from pyscipopt import Model, quicksum

DIGITS = "ABCDEFGHI"


def build(instance):
    m = Model()

    # one-hot binaries: x[d, v] = 1 if digit d takes value v (values 1..9, zero excluded)
    x = {(d, v): m.addVar(name=f"x_{d}_{v}", vtype="B") for d in DIGITS for v in range(1, 10)}
    for d in DIGITS:
        # each digit takes exactly one non-zero value
        m.addCons(quicksum(x[d, v] for v in range(1, 10)) == 1, name=f"one_value_{d}")
    for v in range(1, 10):
        # the nine digits are pairwise distinct: each value is used at most once
        m.addCons(quicksum(x[d, v] for d in DIGITS) <= 1, name=f"distinct_{v}")

    dig = {
        d: m.addVar(name=d, vtype="I", lb=1, ub=9) for d in DIGITS
    }
    for d in DIGITS:
        # link the integer digit to its one-hot encoding
        m.addCons(dig[d] == quicksum(v * x[d, v] for v in range(1, 10)), name=f"link_{d}")

    # two-digit numbers BC, EF, HI (tens digit times 10 plus units digit)
    bc = m.addVar(name="BC", vtype="I", lb=11, ub=99)
    ef = m.addVar(name="EF", vtype="I", lb=11, ub=99)
    hi = m.addVar(name="HI", vtype="I", lb=11, ub=99)
    m.addCons(bc == 10 * dig["B"] + dig["C"], name="BC_value")
    m.addCons(ef == 10 * dig["E"] + dig["F"], name="EF_value")
    m.addCons(hi == 10 * dig["H"] + dig["I"], name="HI_value")

    # A/BC + D/EF + G/HI = 1, multiplied out by BC * EF * HI to avoid division
    # (each term is a digit times the product of the two other two-digit numbers)
    m.addCons(
        dig["A"] * ef * hi + dig["D"] * bc * hi + dig["G"] * bc * ef == bc * ef * hi,
        name="fractions_sum_to_one",
    )

    # the output is the digit values in the order A..I
    outputs = {d: dig[d] for d in DIGITS}
    return m, outputs
