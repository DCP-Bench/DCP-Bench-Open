# Archery puzzle: hit the targets with a number of arrows each so that the total score is as
# close as possible to the target score.
# PySAT only decides satisfiability, so the deviation to minimise is returned as the objective
# (the runner refuses a returned objective instead of ignoring it).
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    targets = instance["targets"]
    target_score = instance["target_score"]
    n = len(targets)

    pool = IDPool()
    # hits[i] = number of arrows on target i; score = total score; deviation = |target - score|
    hits = [Integer(f"hits{i}", 0, target_score, vpool=pool) for i in range(n)]
    score = Integer("score", 0, 2 * target_score, vpool=pool)
    deviation = Integer("deviation", 0, 2 * target_score, vpool=pool)
    engine = IntegerEngine(vars=hits + [score, deviation], vpool=pool)

    engine.add_linear(score - sum(targets[i] * hits[i] for i in range(n)) == 0)
    engine.add_linear(deviation + score >= target_score)   # deviation >= target_score - score
    engine.add_linear(deviation - score >= -target_score)  # deviation >= score - target_score

    return engine.clausify(), {"hits": hits}, ("minimize", deviation)
