# Make the exact amount from the available coins, using as few coins as possible.
from hermax.model import Model


def build(instance):
    amount = instance["amount"]
    types = instance["types_of_coins"]
    available = instance["available_coins"]
    n = len(types)

    m = Model()
    # Each count is capped by what is available and by what the amount allows.
    caps = [min(available[i], amount // types[i] if types[i] else available[i])
            for i in range(n)]
    counts = [m.int(f"count_{i}", 0, caps[i]) for i in range(n)]
    m &= (sum(types[i] * counts[i] for i in range(n)) == amount)
    m.obj += sum(counts)
    return m, {"coin_counts": counts}
