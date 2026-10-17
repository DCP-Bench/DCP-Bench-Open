# Aircraft landing problem: schedule the landing time of each aircraft on one runway,
# following a fixed landing sequence (aircraft i lands before aircraft j when i < j).
# Minimise the total penalty for landing before or after the target time (linear, one unit cost per minute off target).
import cvc5.pythonic as cz


def build(instance):
    earliest = instance["earliest_landing"]
    latest = instance["latest_landing"]
    target = instance["target_landing"]
    pen_before = instance["penalty_before"]
    pen_after = instance["penalty_after"]
    sep = instance["separation_time"]
    n = len(target)

    t = [cz.Int(f"t{i}") for i in range(n)]
    constraints = []

    # Each aircraft lands within its time window.
    # Landing times must respect the earliest and latest landing time of each aircraft.
    for i in range(n):
        constraints.append(t[i] >= earliest[i])
        constraints.append(t[i] <= latest[i])

    # Separation between landings of any two aircraft must be respected.
    # The sequence is fixed, so each later aircraft lands at least the separation time after each earlier one.
    for i in range(n):
        for j in range(i + 1, n):
            constraints.append(t[j] - t[i] >= sep[i][j])

    # Penalties are incurred for landing earlier or later than the target time.
    # Each unit of earliness costs penalty_before, each unit of lateness costs penalty_after.
    penalties = []
    for i in range(n):
        early = pen_before[i] * (target[i] - t[i])
        late = pen_after[i] * (t[i] - target[i])
        penalties.append(cz.If(t[i] < target[i], early, cz.If(t[i] > target[i], late, 0)))
    total = cz.Sum(penalties)

    return constraints, {"landing_times": t, "total_penalty": total}, ("minimize", total)
