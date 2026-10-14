# CMO 2012 problem: find positive integers a >= b with a - b a prime and a * b a
# perfect square n^2, taking the smallest a that is no less than a given minimum.
from pychoco.model import Model


def primes_below(limit):
    """All primes less than limit, by trial division."""
    result = []
    for k in range(2, limit):
        if all(k % d != 0 for d in range(2, int(k ** 0.5) + 1)):
            result.append(k)
    return result


def build(instance):
    min_a = instance["min_a"]  # a must be at least this
    max_val = instance["max_val"]  # upper bound on every variable

    model = Model()

    a = model.intvar(min_a, max_val, name="a")
    b = model.intvar(1, max_val, name="b")  # b is larger than 0
    n = model.intvar(0, max_val, name="n")
    # p = a - b, which has to be a prime: its domain is the list of primes below max_val
    p = model.intvar(primes_below(max_val), name="p")

    # a is not smaller than b
    model.arithm(a, ">=", b).post()
    # the prime p is the difference of a and b
    model.arithm(a, "-", b, "=", p).post()
    # the product a * b is a perfect square, n^2
    product = model.intvar(0, max_val * max_val, name="product")
    model.times(a, b, product).post()
    model.square(product, n).post()

    # the smallest possible a (a is itself a variable, as Choco requires)
    return model, {"a": a, "b": b, "n": n, "p": p}, ("minimize", a)
