from paramita.modelling import Bool


def build(instance):
    # Fifty puzzle (Loyd dummies): a number of little dummies, each with a number
    # on it. Some are knocked over; the numbers on the men knocked down must add
    # up to exactly the target sum.
    values = instance["values"]
    target = instance["target_sum"]
    n = len(values)

    # knocked[i] = 1 if dummy i is knocked over
    knocked = [Bool(f"knocked_{i}") for i in range(n)]

    cons = []
    # the numbers on the dummies knocked over add up to exactly the target sum
    cons.append(sum(v * k for v, k in zip(values, knocked)) == target)

    return cons, {"dummies": knocked}
