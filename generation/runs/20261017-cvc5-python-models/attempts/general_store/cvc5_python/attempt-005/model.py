# general_store: cryptarithm. Each different letter stands for a different digit.
# The words above the line add up to ALL WOOL. Print the values of C, H, E, S, A, B, O, W, P, L.
# Each letter is a one-hot choice among the digits 0 to 9, so that different letters take
# different digits. The addition is encoded column by column, with a carry between columns.
import cvc5.pythonic as cz


def build(instance):
    names = ["C", "H", "E", "S", "A", "B", "O", "W", "P", "L"]
    C, H, E, S, A, B, O, W, P, L = cz.Ints(" ".join(names))
    value = {"C": C, "H": H, "E": E, "S": S, "A": A, "B": B, "O": O, "W": W, "P": P, "L": L}

    constraints = []

    # Each letter is a digit from 0 to 9, chosen by one Boolean per digit; the value is read off these.
    bits = {n: cz.Bools([f"{n}_is_{d}" for d in range(10)]) for n in names}
    for n in names:
        constraints.append(cz.Sum([cz.If(b, 1, 0) for b in bits[n]]) == 1)
        constraints.append(value[n] == cz.Sum([cz.If(bits[n][d], d, 0) for d in range(10)]))
    for d in range(10):
        constraints.append(cz.Sum([cz.If(bits[n][d], 1, 0) for n in names]) == 1)
    # Each different letter stands for a different digit: pairwise different values.
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            constraints.append(value[names[i]] != value[names[j]])

    # The words above the horizontal line add up to ALL WOOL.
    words = [
        [C, H, E, S, S],          # CHESS
        [C, A, S, H],             # CASH
        [B, O, W, W, O, W],       # BOWWOW
        [C, H, O, P, S],          # CHOPS
        [A, L, S, O, P, S],       # ALSOPS
        [P, A, L, E, A, L, E],    # PALEALE
        [C, O, O, L],             # COOL
        [B, A, S, S],             # BASS
        [H, O, P, S],             # HOPS
        [A, L, E, S],             # ALES
        [H, O, E, S],             # HOES
        [A, P, P, L, E, S],       # APPLES
        [C, O, W, S],             # COWS
        [C, H, E, E, S, E],       # CHEESE
        [C, H, S, O, A, P],       # CHSOAP
        [S, H, E, E, P],          # SHEEP
    ]
    total = [A, L, L, W, O, O, L]  # ALLWOOL

    # Column by column from the units digit, the digits of the summands,
    # plus the carry in, equal the digit of the total plus ten times the carry out.
    # A column holds at most 16 digits of at most 9, so a carry is at most 15.
    ncols = len(total)
    carry = [0] * (ncols + 1)
    for k in range(ncols):
        col_terms = [w[-1 - k] for w in words if len(w) > k]
        if k + 1 < ncols:
            carry[k + 1] = cz.Int(f"carry_{k + 1}")
            constraints += [carry[k + 1] >= 0, carry[k + 1] <= 15]
        col_sum = col_terms if k == 0 else col_terms + [carry[k]]
        out_carry = carry[k + 1] if k + 1 < ncols else 0
        constraints.append(cz.Sum(col_sum) == total[-1 - k] + 10 * out_carry)

    solver = cz.SolverFor("QF_LIA")
    solver.add(*constraints)
    outputs = {"A": A, "B": B, "C": C, "E": E, "H": H, "L": L, "O": O, "P": P, "S": S, "W": W}
    return solver, outputs
