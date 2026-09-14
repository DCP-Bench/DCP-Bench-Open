import itertools

from ortools.sat.python import cp_model


def build(instance):
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    n = instance["n_containers"]
    width, length = instance["width"], instance["length"]
    classes, separation = instance["classes"], instance["separation"]

    model = cp_model.CpModel()
    left = [model.new_int_var(0, deck_width, f"left_{i}") for i in range(n)]
    right = [model.new_int_var(0, deck_width, f"right_{i}") for i in range(n)]
    top = [model.new_int_var(0, deck_length, f"top_{i}") for i in range(n)]
    bottom = [model.new_int_var(0, deck_length, f"bottom_{i}") for i in range(n)]

    for i in range(n):
        # Either orientation of the container.
        upright = model.new_bool_var(f"upright_{i}")
        model.add(right[i] - left[i] == width[i]).only_enforce_if(upright)
        model.add(top[i] - bottom[i] == length[i]).only_enforce_if(upright)
        model.add(right[i] - left[i] == length[i]).only_enforce_if(~upright)
        model.add(top[i] - bottom[i] == width[i]).only_enforce_if(~upright)

    for x, y in itertools.combinations(range(n), 2):
        sep = separation[classes[x] - 1][classes[y] - 1]
        apart = [(right[x] + sep, left[y]), (right[y] + sep, left[x]),
                 (top[x] + sep, bottom[y]), (top[y] + sep, bottom[x])]
        literals = []
        for k, (lower, upper) in enumerate(apart):
            literal = model.new_bool_var(f"apart_{x}_{y}_{k}")
            model.add(lower <= upper).only_enforce_if(literal)
            literals.append(literal)
        model.add_bool_or(literals)
    return model, {"left": left, "right": right, "top": top, "bottom": bottom}
