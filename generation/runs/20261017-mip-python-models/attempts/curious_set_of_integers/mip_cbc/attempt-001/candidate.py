# Problem: curious_set_of_integers. The integers 1, 3, 8 and 120 form a set in which the
# product of any two integers is one less than a perfect square. Find a fifth number x
# (x >= 0) that can be added to the set without destroying this property.
import math

import mip

SET = [1, 3, 8, 120]


def build(instance):
    max_val = instance["max_val"]

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    model.verbose = 0
    model.max_mip_gap = 0.0
    model.max_mip_gap_abs = 0.0

    # Find a fifth number (larger than or equal to 0) that can be added to the set
    # without destroying this property.
    x = model.add_var("number", lb=0, ub=max_val, var_type=mip.INTEGER)

    # the product of any two integers is one less than a perfect square
    # (for each a in the set, a * x + 1 is a perfect square s * s; s is chosen one-hot)
    top = math.isqrt(max(SET) * max_val + 1)
    for a in SET:
        pick = [model.add_var(var_type=mip.BINARY) for _ in range(top + 1)]
        model.add_constr(mip.xsum(pick) == 1)
        model.add_constr(mip.xsum(k * k * pick[k] for k in range(top + 1)) == a * x + 1)

    return model, {"number": x}
