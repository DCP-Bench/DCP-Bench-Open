# General store sign puzzle: the letters of a sum of 16 words equal the letters of ALL WOOL.
# Each different letter stands for a different digit. The words above the horizontal line
# represent numbers that add to the total of 'ALL WOOL'. Declared outputs are the digits of
# A, B, C, E, H, L, O, P, S, W.
import mip

ADDENDS = [
    "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
    "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP",
]
TOTAL = "ALLWOOL"
LETTERS = ["A", "B", "C", "E", "H", "L", "O", "P", "S", "W"]


def build(instance):
    model = mip.Model(solver_name="CBC")
    digits = range(10)

    # One-hot choice of digit for each letter: p[L][d] = 1 when letter L stands for digit d.
    p = {L: {d: model.add_var(name=f"p_{L}_{d}", var_type=mip.BINARY) for d in digits}
         for L in LETTERS}
    # The digit of each letter, tied to its one-hot choice.
    x = {L: model.add_var(name=f"x_{L}", lb=0, ub=9, var_type=mip.INTEGER) for L in LETTERS}

    # Each letter stands for exactly one digit.
    for L in LETTERS:
        model.add_constr(mip.xsum(p[L][d] for d in digits) == 1)
        model.add_constr(x[L] == mip.xsum(d * p[L][d] for d in digits))

    # Each different letter stands for a different digit.
    for d in digits:
        model.add_constr(mip.xsum(p[L][d] for L in LETTERS) <= 1)

    # The words above the horizontal line represent numbers that add to the total of 'ALL WOOL'.
    # Column addition from the units place upward, with a carry into the next column.
    width = max(len(w) for w in ADDENDS + [TOTAL])
    carry = [model.add_var(name=f"carry_{k}", lb=0, ub=15, var_type=mip.INTEGER)
             for k in range(width)]
    # Sixteen digits of at most 9, plus a carry of at most 15, give a carry of at most 15.
    # The total has no place beyond the last column, so the top carry is zero.
    model.add_constr(carry[width - 1] == 0)
    for k in range(width):
        # Coefficient of each letter in column k: its count among the addends minus
        # its count in the total.
        coef = {}
        for word in ADDENDS:
            if k < len(word):
                ch = word[len(word) - 1 - k]
                coef[ch] = coef.get(ch, 0) + 1
        ch_total = TOTAL[len(TOTAL) - 1 - k]
        coef[ch_total] = coef.get(ch_total, 0) - 1
        terms = [c * x[L] for L, c in coef.items() if c != 0]
        if k > 0:
            terms.append(carry[k - 1])
        terms.append(-10 * carry[k])
        model.add_constr(mip.xsum(terms) == 0)

    outputs = {L: x[L] for L in LETTERS}
    return model, outputs
