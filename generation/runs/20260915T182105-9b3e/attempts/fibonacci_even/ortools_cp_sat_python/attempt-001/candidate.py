from ortools.sat.python import cp_model


def build(instance):
    """Fibonacci even: sum the even Fibonacci terms below four million.

    The puzzle states its own sequence and cutoff, so `instance` is unused.
    Thirty-five terms is enough to pass four million comfortably.
    """
    del instance

    n = 35
    cutoff = 4000000
    upper = 10000000

    model = cp_model.CpModel()
    f = [model.new_int_var(0, upper, f"f{i}") for i in range(n + 1)]
    x = [model.new_bool_var(f"x{i}") for i in range(n + 1)]
    res = model.new_int_var(0, 100000000, "res")

    model.add(f[0] == 0)
    model.add(f[1] == 1)
    model.add(f[2] == 1)
    model.add(x[0] == 0)
    for i in range(3, n + 1):
        model.add(f[i] == f[i - 1] + f[i - 2])

    terms = []
    for i in range(1, n + 1):
        # A term counts exactly when it is even and below the cutoff.
        remainder = model.new_int_var(0, 1, f"rem{i}")
        model.add_modulo_equality(remainder, f[i], 2)
        even = model.new_bool_var(f"even{i}")
        model.add(remainder == 0).only_enforce_if(even)
        model.add(remainder == 1).only_enforce_if(~even)

        small = model.new_bool_var(f"small{i}")
        model.add(f[i] < cutoff).only_enforce_if(small)
        model.add(f[i] >= cutoff).only_enforce_if(~small)

        model.add_bool_and([even, small]).only_enforce_if(x[i])
        model.add_bool_or([~even, ~small]).only_enforce_if(~x[i])

        # Contribute the term itself when it counts, otherwise nothing.
        term = model.new_int_var(0, upper, f"term{i}")
        model.add(term == f[i]).only_enforce_if(x[i])
        model.add(term == 0).only_enforce_if(~x[i])
        terms.append(term)

    model.add(res == sum(terms))

    return model, {"res": res}
