"""Just forgotten: recover an account number that uses each digit 0..n-1 once, knowing how many digits of each tried set were in place."""
from docplex.mp.model import Model


def build(instance):
    sets = instance["sets"]  # the numbers Joe tried
    correct = instance["num_correct_digits"]
    n = len(sets[0])
    positions = range(n)
    digits = range(n)

    model = Model("just_forgotten")

    # digit_at[i, d] is 1 when position i of the account number holds digit d.
    digit_at = model.binary_var_matrix(positions, digits, name="digit_at")

    # Every position holds one digit, and every digit 0..n-1 is used once.
    for i in positions:
        model.add_constraint(model.sum(digit_at[i, d] for d in digits) == 1, ctname=f"position_{i}")
    for d in digits:
        model.add_constraint(model.sum(digit_at[i, d] for i in positions) == 1, ctname=f"digit_{d}")

    # In each tried set, exactly the given number of digits are in their correct position.
    for k, tried in enumerate(sets):
        model.add_constraint(model.sum(digit_at[i, tried[i]] for i in positions if tried[i] in digits)
                             == correct, ctname=f"set_{k}")

    x = [model.sum(d * digit_at[i, d] for d in digits) for i in positions]
    return model, {"x": x}
