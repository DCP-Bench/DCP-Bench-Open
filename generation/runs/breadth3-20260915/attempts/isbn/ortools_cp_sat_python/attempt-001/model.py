from ortools.sat.python import cp_model


def build(instance):
    given = instance["isbn_init"]
    n = len(given)
    model = cp_model.CpModel()
    isbn = [model.new_int_var(0, 9, f"d_{i}") for i in range(n)]
    # A -1 in the instance marks the digit to find.
    for i in range(n):
        if given[i] != -1:
            model.add(isbn[i] == given[i])
    model.add(isbn[0] == 9)
    model.add(isbn[1] == 7)
    model.add_allowed_assignments([isbn[2]], [(8,), (9,)])
    check = sum(isbn[i] * (1 if i % 2 == 0 else 3) for i in range(n - 1))
    # CP-SAT needs the modulo staged through its own variables.
    remainder = model.new_int_var(0, 9, "remainder")
    model.add_modulo_equality(remainder, check, 10)
    complement = model.new_int_var(1, 10, "complement")
    model.add(complement == 10 - remainder)
    model.add_modulo_equality(isbn[n - 1], complement, 10)
    return model, {"isbn": isbn}
