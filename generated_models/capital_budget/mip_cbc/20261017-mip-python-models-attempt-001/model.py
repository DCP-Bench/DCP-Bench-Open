# Capital budget problem: choose a set of investments, each with a net present
# value (npv) and a cash outflow (cash_flow), so that the total outflow fits in
# the budget and the total npv is as large as possible.
import mip


def build(instance):
    budget = instance["budget"]
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    n = len(npv)
    total_npv = sum(npv)

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # x[i] = 1 if investment i is chosen
    x = [model.add_var(f"x_{i}", var_type=mip.BINARY) for i in range(n)]
    # z = total NPV of the chosen investments; bounded by the sum of all npv values
    z = model.add_var("z", lb=0, ub=total_npv, var_type=mip.INTEGER)

    # the sum of the cash outflows of all chosen investments must not exceed the budget
    model += mip.xsum(cash_flow[i] * x[i] for i in range(n)) <= budget

    # the total npv equals the sum of the npv of the chosen investments
    model += z == mip.xsum(npv[i] * x[i] for i in range(n))

    # the objective is to maximize the total npv
    model.objective = z

    return model, {"x": x, "z": z}
