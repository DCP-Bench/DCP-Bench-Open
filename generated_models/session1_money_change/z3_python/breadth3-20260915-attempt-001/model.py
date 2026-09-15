import z3


def build(instance):
    amount, types, available = (instance["amount"], instance["types_of_coins"],
                                instance["available_coins"])
    n = len(types)
    counts = [z3.Int(f"c_{i}") for i in range(n)]
    constraints = [c >= 0 for c in counts] + [c <= max(available) for c in counts]
    constraints.append(z3.Sum([counts[i] * types[i] for i in range(n)]) == amount)
    constraints += [counts[i] <= available[i] for i in range(n)]
    return constraints, {"coin_counts": counts}, ("minimize", z3.Sum(counts))
