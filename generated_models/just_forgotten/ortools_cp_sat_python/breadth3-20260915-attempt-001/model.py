from ortools.sat.python import cp_model


def build(instance):
    guesses, correct = instance["sets"], instance["num_correct_digits"]
    n = len(guesses[0])
    model = cp_model.CpModel()
    x = [model.new_int_var(0, n - 1, f"x_{i}") for i in range(n)]
    model.add_all_different(x)
    for g, guess in enumerate(guesses):
        hits = []
        for i in range(n):
            hit = model.new_bool_var(f"hit_{g}_{i}")
            model.add(x[i] == guess[i]).only_enforce_if(hit)
            model.add(x[i] != guess[i]).only_enforce_if(~hit)
            hits.append(hit)
        model.add(sum(hits) == correct)
    return model, {"x": x}
