# Curious set of integers: 1, 3, 8 and 120 have the property that the product of any two is one
# less than a perfect square. Find a further number (at least 0) that keeps the property.
from pychoco.model import Model

# The known set 1, 3, 8, 120 is part of the puzzle statement.
KNOWN = [1, 3, 8, 120]


def build(instance):
    n = instance["n"]  # size of the set, the known numbers included
    max_val = instance["max_val"]  # upper bound on the numbers and on the square roots

    model = Model()

    # x[i] = the i-th number of the set; the last one is the number asked for
    x = [model.intvar(0, max_val, name=f"x_{i}", bounded_domain=True) for i in range(n)]

    # The numbers of the set are all different.
    model.all_different(x).post()

    # The first numbers are the known set.
    for i, v in enumerate(KNOWN):
        model.arithm(x[i], "=", v).post()

    # The product of any two numbers is one less than a perfect square: x_i * x_j + 1 = p^2 with
    # the root p in 0..max_val. The product is symmetric, so each unordered pair is stated once.
    # A product with a known number is linear, so it is posted as a weighted sum, not as `times`.
    for i in range(n):
        for j in range(i + 1, n):
            root = model.intvar(0, max_val, name=f"root_{i}_{j}", bounded_domain=True)
            square = model.intvar(0, max_val * max_val, name=f"square_{i}_{j}", bounded_domain=True)
            model.square(square, root).post()
            if i < len(KNOWN):
                # square = KNOWN[i] * x_j + 1
                model.scalar([square, x[j]], [1, -KNOWN[i]], "=", 1).post()
            else:
                product = model.intvar(0, max_val * max_val, name=f"product_{i}_{j}",
                                       bounded_domain=True)
                model.times(x[i], x[j], product).post()
                model.scalar([square, product], [1, -1], "=", 1).post()

    return model, {"number": x[n - 1]}
