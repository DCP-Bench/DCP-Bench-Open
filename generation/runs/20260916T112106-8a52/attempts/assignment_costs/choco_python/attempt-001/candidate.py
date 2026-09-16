from pychoco.model import Model


def build(instance):
    """Assignment costs: every task goes to exactly one person and no person
    takes two tasks, at minimum total cost.
    """
    cost = instance["cost"]
    rows = len(cost)
    cols = len(cost[0]) if rows else 0

    model = Model()
    x = [[model.boolvar(name=f"x{i}_{j}") for j in range(cols)] for i in range(rows)]

    # Exactly one assignment per task; at most one per person.
    for i in range(rows):
        model.sum(x[i], "=", 1).post()
    for j in range(cols):
        model.sum([x[i][j] for i in range(rows)], "<=", 1).post()

    flat = [x[i][j] for i in range(rows) for j in range(cols)]
    prices = [cost[i][j] for i in range(rows) for j in range(cols)]
    total = model.intvar(0, sum(prices), name="total_cost")
    model.scalar(flat, prices, "=", total).post()

    return model, {"x": x}, ("minimize", total)
