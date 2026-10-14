"""Guards and apples: how many apples the boy had before each gate, if each guard takes half plus one."""
from docplex.mp.model import Model


def build(instance):
    gates = instance["num_gates"]

    model = Model("guards_and_apples")

    # apples[i] is the apples he has before gate i, and apples[gates] after the
    # last gate; the reference model declares 0..100 for each.
    apples = model.integer_var_list(gates + 1, 0, 100, name="apples")

    # After the last gate he has the one apple he gives to the girl.
    model.add_constraint(apples[gates] == 1, ctname="for_the_girl")

    # Each guard takes half of the apples plus one, so what he had was twice
    # what he keeps plus two.
    for i in range(1, gates + 1):
        model.add_constraint(apples[i - 1] == 2 * (apples[i] + 1), ctname=f"gate_{i}")

    return model, {"apples": apples}
