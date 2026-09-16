import pulp


def build(instance):
    """Map colouring: adjacent countries differ in colour, and the highest
    colour number used is as small as possible.
    """
    graph = instance["graph"]
    # The instance carries only the edge list, so the country count is the
    # largest 1-based country id appearing in it.
    num_nodes = max(max(edge) for edge in graph)
    # Colours run 1..num_nodes, as in the reference.
    colours = range(1, num_nodes + 1)

    problem = pulp.LpProblem("colouring", pulp.LpMinimize)
    # A colour cannot be compared for inequality directly, so the model picks
    # one colour per country and forbids a shared pick along each edge.
    pick = pulp.LpVariable.dicts("pick", (range(num_nodes), colours), cat="Binary")

    for i in range(num_nodes):
        problem += pulp.lpSum(pick[i][c] for c in colours) == 1
    for first, second in graph:
        for c in colours:
            problem += pick[first - 1][c] + pick[second - 1][c] <= 1

    colors = [pulp.LpVariable(f"colour{i}", 1, num_nodes, cat="Integer")
              for i in range(num_nodes)]
    for i in range(num_nodes):
        problem += colors[i] == pulp.lpSum(c * pick[i][c] for c in colours)

    highest = pulp.LpVariable("highest", 1, num_nodes, cat="Integer")
    for i in range(num_nodes):
        problem += highest >= colors[i]
    problem += highest

    return problem, {"colors": colors}
