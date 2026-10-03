"""Hardy 1729, squares version: four different numbers a, b, c, d in 1..100 with
a^2 + b^2 = c^2 + d^2.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; the range 1..100 is from the statement.
    range_min, range_max = 1, 100
    names = "abcd"
    values = range(range_min, range_max + 1)

    model = Model("hardy_1729_square")

    # is_value[x, v] is 1 when number x is v. CPLEX refuses x * x == ..., so each number is
    # chosen from its values and its square is read as sum of v * v over the choice.
    is_value = {(x, v): model.binary_var(name=f"{x}_is_{v}") for x in names for v in values}
    for x in names:
        model.add_constraint(model.sum(is_value[x, v] for v in values) == 1)

    # The four numbers are all different: no value is taken twice.
    for v in values:
        model.add_constraint(model.sum(is_value[x, v] for x in names) <= 1)

    def square(x):
        return model.sum(v * v * is_value[x, v] for v in values)

    # a^2 + b^2 = c^2 + d^2.
    model.add_constraint(square("a") + square("b") == square("c") + square("d"))

    number = {x: model.integer_var(range_min, range_max, name=x) for x in names}
    for x in names:
        model.add_constraint(number[x] == model.sum(v * is_value[x, v] for v in values))

    return model, dict(number)
