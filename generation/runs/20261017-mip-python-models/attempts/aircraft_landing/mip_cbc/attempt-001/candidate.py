# Aircraft Landing Problem: schedule the landing of a set of aircraft on a single runway.
# Each aircraft has a time window (earliest and latest landing time) and a target landing time.
# Penalties are incurred for landing earlier or later than the target. The landing sequence is fixed
# (the index order). Minimise the total penalty.
import mip


def build(instance):
    earliest = instance["earliest_landing"]
    latest = instance["latest_landing"]
    target = instance["target_landing"]
    penalty_before = instance["penalty_before"]
    penalty_after = instance["penalty_after"]
    separation = instance["separation_time"]
    n = len(target)

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Each aircraft lands at an integer time within its time window.
    x = [m.add_var(f"x_{i}", lb=earliest[i], ub=latest[i], var_type=mip.INTEGER) for i in range(n)]

    # Earliness and tardiness of each aircraft with respect to its target landing time.
    early = [
        m.add_var(f"early_{i}", lb=0, ub=max(target[i] - earliest[i], 0), var_type=mip.INTEGER)
        for i in range(n)
    ]
    late = [
        m.add_var(f"late_{i}", lb=0, ub=max(latest[i] - target[i], 0), var_type=mip.INTEGER)
        for i in range(n)
    ]

    # Penalties are incurred for landing earlier or later than the target time.
    # Earliness is the amount before the target, tardiness the amount after it.
    for i in range(n):
        m += early[i] >= target[i] - x[i]
        m += late[i] >= x[i] - target[i]

    # A minimum separation time between the landings of any two aircraft must be respected.
    # The landing sequence is fixed: aircraft i lands before aircraft j for i < j.
    for i in range(n):
        for j in range(i + 1, n):
            m += x[j] >= x[i] + separation[i][j]

    # Total penalty: the penalty before the target and the penalty after the target, summed over the aircraft.
    max_total = sum(
        penalty_before[i] * max(target[i] - earliest[i], 0)
        + penalty_after[i] * max(latest[i] - target[i], 0)
        for i in range(n)
    )
    total = m.add_var("total_penalty", lb=0, ub=max_total, var_type=mip.INTEGER)
    m += total == mip.xsum(
        penalty_before[i] * early[i] + penalty_after[i] * late[i] for i in range(n)
    )

    # Minimise the total penalty.
    m.objective = total

    return m, {"landing_times": x, "total_penalty": total}
