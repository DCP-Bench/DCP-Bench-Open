# Broken weights: a weight of m pounds broke into n pieces of whole-pound
# weights. Find piece weights that let a balance scale weigh every whole weight
# from 1 to m, where a piece may go on the same pan as the object, on the other
# pan, or stay off the scale.
from ortools.sat.python import cp_model


def build(instance):
    m = instance["m"]  # weight of the unbroken weight
    n = instance["n"]  # number of pieces

    model = cp_model.CpModel()

    # weights[j] = the weight of piece j
    weights = [model.new_int_var(1, m, f"weights_{j}") for j in range(n)]

    # the pieces together weigh m
    model.add(sum(weights) == m)

    # every weight 1..m can be weighed. Each piece is placed on one pan (+1),
    # the other pan (-1) or not used (0), and the signed weights add up to the
    # weight being measured. The signed weight of a piece is chosen with two
    # Booleans instead of multiplying the weight by a variable.
    for target in range(1, m + 1):
        signed = []
        for j in range(n):
            on_first = model.new_bool_var(f"first_pan_{target}_{j}")
            on_second = model.new_bool_var(f"second_pan_{target}_{j}")
            model.add_at_most_one([on_first, on_second])
            term = model.new_int_var(-m, m, f"term_{target}_{j}")
            model.add(term == weights[j]).only_enforce_if(on_first)
            model.add(term == -weights[j]).only_enforce_if(on_second)
            model.add(term == 0).only_enforce_if([on_first.negated(), on_second.negated()])
            signed.append(term)
        model.add(sum(signed) == target)

    return model, {"weights": weights}
