from ortools.sat.python import cp_model


def build(instance):
    total, items = instance["total_price"], instance["num_items"]
    model = cp_model.CpModel()
    prices = [model.new_int_var(1, total, f"p_{i}") for i in range(items)]
    model.add(sum(prices) == total)
    # CP-SAT multiplies two terms at a time, so the product is built up.
    running = prices[0]
    for i in range(1, items):
        nxt = model.new_int_var(1, total ** (i + 1), f"product_{i}")
        model.add_multiplication_equality(nxt, [running, prices[i]])
        running = nxt
    model.add(running == total * 100 ** (items - 1))
    return model, {"prices": prices}
