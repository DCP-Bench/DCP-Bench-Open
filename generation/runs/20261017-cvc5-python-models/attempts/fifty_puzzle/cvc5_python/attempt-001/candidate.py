# Fifty puzzle (side show): choose a subset of dummies whose numbers sum exactly to the target sum.
# Output: dummies, one Boolean per dummy, true when the dummy is knocked over.

import cvc5.pythonic as cz


def build(instance):
    values = instance["values"]
    target = instance["target_sum"]
    n = len(values)

    dummies = cz.Bools(" ".join(f"d{i}" for i in range(n)))

    # The numbers on the dummies knocked over add up to exactly the target sum.
    # Add up the numbers on all the men that you knock down and when the sum amounts to exactly a given target sum, neither more nor less you get a genuine prize.
    total = cz.Sum([cz.If(dummies[i], values[i], 0) for i in range(n)])
    constraints = [total == target]

    return constraints, {"dummies": dummies}
