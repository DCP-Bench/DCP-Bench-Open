# General store puzzle: the cryptarithm of the sixteen words above the line adding up to ALL WOOL,
# where each different letter stands for a different digit.
from pyscipopt import Model, quicksum

# The words above the line and the total, as written in the problem statement (problem data, not instance data).
WORDS = ["CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
         "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"]
TOTAL = "ALLWOOL"
LETTERS = "ABCEHLOPSW"  # the ten distinct letters of the puzzle
WIDTH = len(TOTAL)      # the total has the most digits: seven columns


def build(instance):
    m = Model()

    # b[L, v] = 1 if letter L stands for digit v; a digit expression d[L] is derived from it
    b = {(L, v): m.addVar(name=f"b_{L}_{v}", vtype="B") for L in LETTERS for v in range(10)}
    d = {}
    for L in LETTERS:
        # each letter stands for exactly one digit
        m.addCons(quicksum(b[L, v] for v in range(10)) == 1)
        d[L] = quicksum(v * b[L, v] for v in range(10))

    # each digit is used by exactly one letter (ten letters, ten digits, all different)
    for v in range(10):
        m.addCons(quicksum(b[L, v] for L in LETTERS) == 1)

    # carry[p] is the carry into column p (column 0 is the units column); the carries out of the
    # first column and of the last column are zero. A column holds at most 16 digits of at most 9,
    # so a carry never exceeds 15.
    carry = {p: m.addVar(name=f"carry_{p}", vtype="I", lb=0, ub=16) for p in range(1, WIDTH)}

    # the column additions: the digits of the sixteen words in each column, plus the carry in,
    # equal the total's digit in that column plus ten times the carry out
    for p in range(WIDTH):
        rows = [w[len(w) - 1 - p] for w in WORDS if p < len(w)]
        cin = carry[p] if p > 0 else 0
        cout = carry[p + 1] if p + 1 < WIDTH else 0
        # the words' digits and the carry from the column before add up to the total's digit
        m.addCons(quicksum(d[L] for L in rows) + cin == d[TOTAL[WIDTH - 1 - p]] + 10 * cout)

    outputs = {
        "A": d["A"], "B": d["B"], "C": d["C"], "E": d["E"], "H": d["H"],
        "L": d["L"], "O": d["O"], "P": d["P"], "S": d["S"], "W": d["W"],
    }
    return m, outputs
