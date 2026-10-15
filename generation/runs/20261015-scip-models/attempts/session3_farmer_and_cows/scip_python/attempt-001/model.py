# Farmer and cows: split numbered cows among sons so each son gets the required number of cows and the same total milk.
from pyscipopt import Model, quicksum


def build(instance):
    num_cows = instance["num_cows"]
    num_sons = instance["num_sons"]
    cows_per_son = instance["cows_per_son"]
    m = Model("farmer_and_cows")

    # x[c, s] = 1 if cow c+1 goes to son s
    x = {(c, s): m.addVar(name=f"x_{c}_{s}", vtype="B") for c in range(num_cows) for s in range(num_sons)}

    # each cow goes to exactly one son
    for c in range(num_cows):
        m.addCons(quicksum(x[c, s] for s in range(num_sons)) == 1)

    # each son receives the number of cows given by the distribution
    for s in range(num_sons):
        m.addCons(quicksum(x[c, s] for c in range(num_cows)) == cows_per_son[s])

    # the milk of cow c+1 is c+1; the total milk of every son is the same
    milk = [quicksum((c + 1) * x[c, s] for c in range(num_cows)) for s in range(num_sons)]
    for s in range(1, num_sons):
        m.addCons(milk[s] == milk[0])

    # output: the son of each cow, numbered from 0
    cow_assignments = [quicksum(s * x[c, s] for s in range(num_sons)) for c in range(num_cows)]
    return m, {"cow_assignments": cow_assignments}
