import cpmpy as cp


def build(instance):
    """Curious set of integers: extend {1, 3, 8, 120}, where the product of
    any two members is one less than a perfect square.
    """
    n = instance["n"]
    max_val = instance["max_val"]

    x = cp.intvar(0, max_val, shape=n, name="x")
    number = x[-1]

    model = cp.Model(cp.AllDifferent(x))
    # The four known members of the set are part of the problem statement.
    known = [1, 3, 8, 120]
    for index, value in enumerate(known):
        model += x[index] == value

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            root = cp.intvar(0, max_val, name=f"root_{i}_{j}")
            model += root * root == x[i] * x[j] + 1

    return model, {"number": number}
