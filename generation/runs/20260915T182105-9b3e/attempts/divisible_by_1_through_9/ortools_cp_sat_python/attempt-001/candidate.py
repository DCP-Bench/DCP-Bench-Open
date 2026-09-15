from ortools.sat.python import cp_model


def build(instance):
    """Divisible by 1 through 9: a ten-digit pandigital number whose first n
    digits form a multiple of n, for every n.

    The puzzle fixes its own ten digits, so `instance` is unused.
    """
    del instance

    digits = 10
    model = cp_model.CpModel()
    x = [model.new_int_var(0, 9, f"x{i}") for i in range(digits)]
    # t[i] is the number formed by the first i + 1 digits.
    t = [model.new_int_var(0, 10 ** digits, f"t{i}") for i in range(digits)]
    number = t[digits - 1]

    model.add_all_different(x)
    for i in range(digits):
        model.add(t[i] == sum(x[j] * (10 ** (i - j)) for j in range(i + 1)))
        # Divisibility as a remainder of zero.
        remainder = model.new_int_var(0, i, f"r{i}")
        model.add_modulo_equality(remainder, t[i], i + 1)
        model.add(remainder == 0)

    return model, {"number": number}
