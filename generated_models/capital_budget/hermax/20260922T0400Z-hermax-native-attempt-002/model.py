# Choose investments to maximise net present value within the budget.
from math import gcd

from hermax.model import Model


def build(instance):
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    budget = instance["budget"]
    n = len(npv)

    m = Model()
    x = m.bool_vector("x", n)
    m &= (sum(cash_flow[j] * x[j] for j in range(n)) <= budget)

    # Maximising: the soft clause is broken by *not* taking an investment, so
    # it pays that investment's value. Minimising what is forgone maximises
    # what is taken.
    for j in range(n):
        m.obj[npv[j]] += x[j]

    # The brief declares the total as an output, so it needs a variable. Its
    # natural range here runs to tens of thousands, and encoding an integer
    # that wide exhausted the memory limit outright. Every value it can take is
    # a multiple of the values' gcd, so the variable counts those units and is
    # scaled back up for the output: 0..29 instead of 0..58000 on the listed
    # instance, which builds and solves in about a second.
    unit = 0
    for value in npv:
        unit = gcd(unit, value)
    units = m.int("units", 0, sum(npv) // unit)
    m &= (sum((npv[j] // unit) * x[j] for j in range(n)) == units)
    z = m.scale(units, unit, name="z")
    return m, {"x": x, "z": z}
