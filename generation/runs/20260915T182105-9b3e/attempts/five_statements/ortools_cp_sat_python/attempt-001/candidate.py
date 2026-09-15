from ortools.sat.python import cp_model


def build(instance):
    """Five self-referential statements, the i-th claiming that exactly i + 1
    of them are false.

    The puzzle states its own five claims, so `instance` is unused.
    """
    del instance

    n = 5
    model = cp_model.CpModel()
    statements = [model.new_bool_var(f"s{i}") for i in range(n)]

    false_count = sum(statements[j].negated() for j in range(n))
    for i in range(n):
        # Statement i holds exactly when the false count is i + 1, so the
        # equivalence is posted in both directions.
        model.add(false_count == i + 1).only_enforce_if(statements[i])
        model.add(false_count != i + 1).only_enforce_if(~statements[i])

    return model, {"statements": statements}
