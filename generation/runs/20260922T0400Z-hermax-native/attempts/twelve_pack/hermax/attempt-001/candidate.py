# Fewest items from whole packs that still meet the target.
from hermax.model import Model


def build(instance):
    packs = instance["packs"]
    target = instance["target"]
    n = len(packs)

    m = Model()
    # No pack is ever needed more often than the target divided by its size,
    # plus one to allow overshooting the target.
    counts = [m.int(f"count_{i}", 0, target // packs[i] + 1) for i in range(n)]
    supplied = sum(packs[i] * counts[i] for i in range(n))
    m &= (supplied >= target)
    m.obj += supplied
    return m, {"counts": counts}
