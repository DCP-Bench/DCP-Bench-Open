# Cabling problem: place the devices of a rack in one order, one device per position,
# so that the sum of all cable lengths is as short as possible. A cable between two
# devices is as long as the distance between their positions, and a device pair may
# carry several cables. Output final_sum: the optimal total cable length.
import mip


def build(instance):
    n = instance["n"]
    devices = instance["devices"]
    index = {name: i for i, name in enumerate(devices)}
    cables = instance["cable_struct"]
    max_dist = n - 1  # largest possible distance between two positions 0..n-1

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Placement: p[i][k] = 1 when device i sits at position k.
    p = [[m.add_var(f"p_{i}_{k}", var_type=mip.BINARY) for k in range(n)]
         for i in range(n)]

    # Each device is placed at exactly one position.
    for i in range(n):
        m += mip.xsum(p[i]) == 1

    # Each position holds exactly one device.
    for k in range(n):
        m += mip.xsum(p[i][k] for i in range(n)) == 1

    # Position of each device, tied to its placement binaries.
    pos = [m.add_var(f"pos_{i}", lb=0, ub=max_dist, var_type=mip.INTEGER)
           for i in range(n)]
    for i in range(n):
        m += pos[i] == mip.xsum(k * p[i][k] for k in range(n))

    # Cable lengths: one distance variable per cable row, bounded by the rack size.
    # The distance between two positions is the absolute difference of their positions;
    # the objective is minimised, so the two lower bounds on d give exactly |a - b|.
    length_terms = []
    total_ub = 0
    for c, (a, b, count) in enumerate(cables):
        ia = index[a]
        ib = index[b]
        d = m.add_var(f"d_{c}", lb=0, ub=max_dist, var_type=mip.INTEGER)
        m += d >= pos[ia] - pos[ib]
        m += d >= pos[ib] - pos[ia]
        length_terms.append(count * d)
        total_ub += count * max_dist

    # Total cable length, an integer output tied to the sum of all cable lengths.
    final_sum = m.add_var("final_sum", lb=0, ub=total_ub, var_type=mip.INTEGER)
    m += final_sum == mip.xsum(length_terms)

    m.objective = final_sum
    return m, {"final_sum": final_sum}
