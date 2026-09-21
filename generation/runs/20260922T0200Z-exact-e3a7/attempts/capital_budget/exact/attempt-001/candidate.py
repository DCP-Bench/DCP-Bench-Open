# Choose investments to maximise net present value within the budget.
from dcp_pb import Pb


def build(instance):
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    budget = instance["budget"]

    pb = Pb()
    x = pb.bools(len(npv))
    pb.weighted_sum_le(cash_flow, x, budget)

    # The brief declares the total as an output, so it needs a variable of its
    # own. Tying it costs one linear constraint; Exact integers are native.
    z = pb.int(0, sum(npv))
    pb.eq(list(zip(npv, x)) + [(-1, z)], 0)
    pb.maximise([(1, z)])
    return pb, {"x": x, "z": z}
