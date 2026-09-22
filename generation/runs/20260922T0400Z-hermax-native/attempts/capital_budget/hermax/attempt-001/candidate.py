# Choose investments to maximise net present value within the budget.
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

    # The brief declares the total as an output, so it needs a variable too.
    z = m.int("z", 0, sum(npv))
    m &= (sum(npv[j] * x[j] for j in range(n)) == z)
    return m, {"x": x, "z": z}
