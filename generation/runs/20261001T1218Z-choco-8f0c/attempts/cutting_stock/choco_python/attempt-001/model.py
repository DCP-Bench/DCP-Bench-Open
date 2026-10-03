# Cutting stock: decide how many times to use each cutting pattern so that the pieces
# produced meet the orders for every width, while minimising the number of raw rolls cut.
from pychoco.model import Model

# Upper bound on how often one pattern can be used. It is a constant of the problem's
# model, not an instance field.
MAX_USES = 100


def build(instance):
    orders = instance["orders"]  # orders[j] = number of pieces of width j that are needed
    num_patterns = instance["num_patterns"]  # number of cutting patterns
    pieces_in_pattern = instance["num_rolls_width"]  # pieces_in_pattern[p][j] = pieces of width j in pattern p
    num_widths = len(orders)

    model = Model()

    # patterns_used[p] = number of raw rolls cut with pattern p
    patterns_used = [model.intvar(0, MAX_USES, name=f"patterns_used_{p}") for p in range(num_patterns)]

    # for each width, the pieces cut over all patterns must meet the orders
    for j in range(num_widths):
        coefficients = [pieces_in_pattern[p][j] for p in range(num_patterns)]
        model.scalar(patterns_used, coefficients, ">=", orders[j]).post()

    # total number of raw rolls cut, the quantity to minimise
    min_rolls_cut = model.intvar(0, MAX_USES * num_patterns, name="min_rolls_cut")
    model.sum(patterns_used, "=", min_rolls_cut).post()

    return model, {"patterns_used": patterns_used, "min_rolls_cut": min_rolls_cut}, ("minimize", min_rolls_cut)
