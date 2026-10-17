# Bank card PIN (session1_bank_card): find the 4-digit PIN abcd.
# Facts: no two digits are the same; the 2-digit number cd is 3 times the
# 2-digit number ab; the 2-digit number da is 2 times the 2-digit number bc.
# Output: a, b, c, d (the PIN digits).
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Digits 0..9; the PIN's first digit is not 0 because ab is a two-digit number.
    a = model.add_var("a", lb=1, ub=9, var_type=mip.INTEGER)
    b = model.add_var("b", lb=0, ub=9, var_type=mip.INTEGER)
    c = model.add_var("c", lb=0, ub=9, var_type=mip.INTEGER)
    d = model.add_var("d", lb=0, ub=9, var_type=mip.INTEGER)
    digits = [a, b, c, d]

    # no two digits are the same
    for i in range(4):
        for j in range(i + 1, 4):
            s = model.add_var(f"s_{i}_{j}", var_type=mip.BINARY)
            # s = 0 gives digits[i] < digits[j]; s = 1 gives digits[j] < digits[i]
            model.add_constr(digits[i] - digits[j] <= -1 + 10 * s)
            model.add_constr(digits[j] - digits[i] <= -1 + 10 * (1 - s))

    # the 2-digit number cd is 3 times the 2-digit number ab
    # 10c + d = 3 * (10a + b)
    model.add_constr(mip.xsum([10 * c, d, -30 * a, -3 * b]) == 0)

    # the 2-digit number da is 2 times the 2-digit number bc
    # 10d + a = 2 * (10b + c)
    model.add_constr(mip.xsum([10 * d, a, -20 * b, -2 * c]) == 0)

    # satisfaction problem: no objective
    return model, {"a": a, "b": b, "c": c, "d": d}
