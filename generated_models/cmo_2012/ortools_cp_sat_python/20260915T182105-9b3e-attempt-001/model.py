from ortools.sat.python import cp_model


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

    model = cp_model.CpModel()
    a = model.new_int_var(min_a, max_val, "a")
    b = model.new_int_var(1, max_val, "b")
    n = model.new_int_var(0, max_val, "n")
    # p is one of the primes below max_val, stated as a domain of exactly those
    # values.
    p = model.new_int_var_from_domain(
        cp_model.Domain.from_values(prime_list), "p"
    )

    model.add(a >= b)
    model.add(p == a - b)

    product = model.new_int_var(0, max_val * max_val, "product")
    square = model.new_int_var(0, max_val * max_val, "square")
    model.add_multiplication_equality(product, [a, b])
    model.add_multiplication_equality(square, [n, n])
    model.add(product == square)

    model.minimize(a)

    return model, {"a": a, "b": b, "n": n, "p": p}
