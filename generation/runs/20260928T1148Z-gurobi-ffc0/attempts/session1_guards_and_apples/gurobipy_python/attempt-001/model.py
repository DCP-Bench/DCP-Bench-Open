"""Guards and apples: how many apples the boy had before each gate, if each guard takes half plus one."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    gates = instance["num_gates"]

    model = gp.Model("guards_and_apples")

    # apples[i] is the apples he has before gate i, and apples[gates] after the
    # last gate; the reference model declares 0..100 for each.
    apples = model.addVars(gates + 1, lb=0, ub=100, vtype=GRB.INTEGER, name="apples")

    # After the last gate he has the one apple he gives to the girl.
    model.addConstr(apples[gates] == 1, name="for_the_girl")

    # Each guard takes half of the apples plus one, so what he had was twice
    # what he keeps plus two.
    for i in range(1, gates + 1):
        model.addConstr(apples[i - 1] == 2 * (apples[i] + 1), name=f"gate[{i}]")

    return model, {"apples": [apples[i] for i in range(gates + 1)]}
