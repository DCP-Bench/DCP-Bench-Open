# Make the exact amount from the available coins, using as few coins as possible.
from dcp_maxsat import MaxSat


def build(instance):
    amount = instance["amount"]
    types = instance["types_of_coins"]
    available = instance["available_coins"]
    n = len(types)

    sat = MaxSat()
    # Each count is capped by what is available and by what the amount allows.
    counts = [sat.int(0, min(available[i], amount // types[i] if types[i] else available[i]))
              for i in range(n)]
    sat.weighted_sum_eq(types, counts, amount)

    used = sat.int(0, sum(min(available[i], amount // types[i] if types[i] else available[i])
                          for i in range(n)))
    sat.link_sum([(1, c) for c in counts], used)
    return sat, {"coin_counts": counts}, ("minimize", used)
