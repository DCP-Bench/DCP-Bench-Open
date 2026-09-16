from pychoco.model import Model


def build(instance):
    """Capital budgeting: choose investments whose combined cash outflow fits
    the budget, maximizing total net present value.
    """
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    budget = instance["budget"]
    n = len(npv)

    model = Model()
    x = [model.boolvar(name=f"x{i}") for i in range(n)]

    model.scalar(x, cash_flow, "<=", budget).post()

    z = model.intvar(0, sum(npv), name="z")
    model.scalar(x, npv, "=", z).post()

    return model, {"z": z, "x": x}, ("maximize", z)
