import z3


def build(instance):
    graph = instance["graph"]
    # The reference fixes the country count; it is the largest 1-based node id.
    nodes = max(max(edge) for edge in graph)
    colors = [z3.Int(f"c_{k}") for k in range(nodes)]
    constraints = [c >= 1 for c in colors] + [c <= nodes for c in colors]
    constraints += [colors[i - 1] != colors[j - 1] for i, j in graph]
    used = z3.Int("used")
    # Minimising pulls `used` down to the largest colour actually taken.
    constraints += [used >= c for c in colors]
    return constraints, {"colors": colors}, ("minimize", used)
