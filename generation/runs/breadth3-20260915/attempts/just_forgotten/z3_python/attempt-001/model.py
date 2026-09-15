import z3


def build(instance):
    guesses, correct = instance["sets"], instance["num_correct_digits"]
    n = len(guesses[0])
    x = [z3.Int(f"x_{i}") for i in range(n)]
    constraints = [v >= 0 for v in x] + [v <= n - 1 for v in x] + [z3.Distinct(x)]
    for guess in guesses:
        constraints.append(z3.Sum([z3.If(x[i] == guess[i], 1, 0) for i in range(n)]) == correct)
    return constraints, {"x": x}
