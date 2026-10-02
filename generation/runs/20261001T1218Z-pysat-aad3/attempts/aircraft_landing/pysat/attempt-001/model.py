# Aircraft landing: choose a landing time in its window for every aircraft, keeping the
# separation times, so that the penalty for landing before or after the target is as small
# as possible.
# PySAT only decides satisfiability, so the penalty to minimise is returned as the objective
# (the runner refuses a returned objective instead of ignoring it).
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    earliest = instance["earliest_landing"]
    latest = instance["latest_landing"]
    target = instance["target_landing"]
    penalty_after = instance["penalty_after"]
    penalty_before = instance["penalty_before"]
    separation = instance["separation_time"]
    n = len(earliest)
    horizon = max(latest)

    pool = IDPool()
    landing = [Integer(f"landing{i}", earliest[i], latest[i], vpool=pool) for i in range(n)]
    earliness = [Integer(f"earliness{i}", 0, horizon, vpool=pool) for i in range(n)]
    lateness = [Integer(f"lateness{i}", 0, horizon, vpool=pool) for i in range(n)]
    penalty = Integer("total_penalty", 0, horizon * n * max(penalty_after + penalty_before), vpool=pool)
    engine = IntegerEngine(vars=landing + earliness + lateness + [penalty], vpool=pool)

    # landing time minus target = lateness minus earliness
    for i in range(n):
        engine.add_linear(landing[i] - lateness[i] + earliness[i] == target[i])
    # aircraft i lands before aircraft j (i < j) with at least the separation time between them
    for i in range(n):
        for j in range(i + 1, n):
            engine.add_linear(landing[j] - landing[i] >= separation[i][j])
    engine.add_linear(penalty - sum(penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i]
                                    for i in range(n)) == 0)

    return engine.clausify(), {"landing_times": landing, "total_penalty": penalty}, ("minimize", penalty)
