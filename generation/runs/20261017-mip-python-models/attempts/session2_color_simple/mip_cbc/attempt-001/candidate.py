# Problem session2_color_simple: colour six countries (Belgium, Denmark, France,
# Germany, Netherlands, Luxembourg) with integers starting from 1 so that two
# neighbouring countries have different colours, minimizing the number of colours used.
# Neighbours come from instance["graph"] as 1-based pairs.
import mip


def build(instance):
    edges = [(u - 1, v - 1) for u, v in instance["graph"]]
    n = 1 + max(max(u, v) for u, v in edges)
    K = n  # at most one colour per country is ever needed

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # x[i][c] = 1 when country i takes colour c+1
    x = [[model.add_var(f"x_{i}_{c}", var_type=mip.BINARY) for c in range(K)] for i in range(n)]
    # colors[i] = colour number of country i
    colors = [model.add_var(f"colors_{i}", lb=1, ub=K, var_type=mip.INTEGER) for i in range(n)]
    # the largest colour number used
    top = model.add_var("top_colour", lb=1, ub=K, var_type=mip.INTEGER)

    # Each country gets exactly one colour.
    for i in range(n):
        model.add_constr(mip.xsum(x[i]) == 1)

    # The colour number of each country.
    for i in range(n):
        model.add_constr(colors[i] == mip.xsum((c + 1) * x[i][c] for c in range(K)))

    # Two neighbouring countries cannot have the same colour.
    for u, v in edges:
        for c in range(K):
            model.add_constr(x[u][c] + x[v][c] <= 1)

    # Minimize the number of colours used: with colours numbered from 1, that is
    # the largest colour number, so every country's colour is at most top.
    for i in range(n):
        model.add_constr(colors[i] <= top)

    model.objective = top

    return model, {"colors": colors}
