import cpmpy as cp


def build(instance):
    guesses, correct = instance["sets"], instance["num_correct_digits"]
    n = len(guesses[0])
    x = cp.intvar(0, n - 1, shape=n, name="x")
    model = cp.Model(cp.AllDifferent(x))
    for guess in guesses:
        model += cp.sum([x[i] == guess[i] for i in range(n)]) == correct
    return model, {"x": [x[i] for i in range(n)]}
