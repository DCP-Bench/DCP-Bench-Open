# Problem cur_num: the number 48 has this peculiarity, that if you add 1 to it the result
# is a square number, and if you add 1 to its half, you also get a square number.
# Print another number with this peculiarity (peculiar) between 1 and 10000.
import math

import mip


def build(instance):
    top = 10000
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    peculiar = model.add_var("peculiar", lb=1, ub=top, var_type=mip.INTEGER)
    half = model.add_var("half", lb=0, ub=top // 2, var_type=mip.INTEGER)

    # the number has a half, so it is even: its half is peculiar / 2
    model.add_constr(peculiar == 2 * half)

    # if you add 1 to the number, the result is a square number
    # (one binary per candidate root k, with k * k the square)
    root_max = math.isqrt(top + 1)
    root = [model.add_var(f"root_{k}", var_type=mip.BINARY) for k in range(root_max + 1)]
    model.add_constr(mip.xsum(root) == 1)
    model.add_constr(mip.xsum(k * k * root[k] for k in range(root_max + 1)) == peculiar + 1)

    # if you add 1 to its half, you also get a square number
    half_root_max = math.isqrt(top // 2 + 1)
    half_root = [model.add_var(f"half_root_{k}", var_type=mip.BINARY) for k in range(half_root_max + 1)]
    model.add_constr(mip.xsum(half_root) == 1)
    model.add_constr(mip.xsum(k * k * half_root[k] for k in range(half_root_max + 1)) == half + 1)

    # print another number: the peculiar number is not 48
    # (z = 0 gives peculiar <= 47, z = 1 gives peculiar >= 49)
    z = model.add_var("not_48", var_type=mip.BINARY)
    model.add_constr(peculiar <= 47 + (top - 47) * z)
    model.add_constr(peculiar >= 49 * z)

    return model, {"peculiar": peculiar}
