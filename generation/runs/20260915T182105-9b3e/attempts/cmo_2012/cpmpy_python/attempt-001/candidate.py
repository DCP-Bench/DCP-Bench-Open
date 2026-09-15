import cpmpy as cp


def build(instance):
    """CMO 2012: the smallest a at or above a minimum such that a - b is prime
    and a * b is a perfect square.
    """
    min_a = instance["min_a"]
    max_val = instance["max_val"]

    def is_prime(value):
        if value < 2:
            return False
        divisor = 2
        while divisor * divisor <= value:
            if value % divisor == 0:
                return False
            divisor += 1
        return True

    prime_list = [value for value in range(2, max_val) if is_prime(value)]

    a = cp.intvar(min_a, max_val, name="a")
    b = cp.intvar(1, max_val, name="b")
    n = cp.intvar(0, max_val, name="n")
    p = cp.intvar(2, max_val, name="p")

    model = cp.Model(
        # p is one of the primes below max_val.
        cp.sum([p == value for value in prime_list]) > 0,
        a >= b,
        p == a - b,
        a * b == n * n,
    )
    model.minimize(a)

    return model, {"a": a, "b": b, "n": n, "p": p}
