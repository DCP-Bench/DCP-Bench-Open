# Colour adjacent countries differently, using as few colours as possible.
from dcp_maxsat import MaxSat


def build(instance):
    graph = instance["graph"]
    # The edge list numbers the countries 1..num_nodes.
    num_nodes = max(max(edge) for edge in graph)

    sat = MaxSat()
    colors = sat.ints(num_nodes, 1, num_nodes)
    for left, right in graph:
        sat.different(colors[left - 1], colors[right - 1])

    # Minimising an upper bound on every colour drives it to the largest one.
    used = sat.int(1, num_nodes)
    for colour in colors:
        sat.linear_le([(1, colour), (-1, used)], 0)
    return sat, {"colors": colors}, ("minimize", used)
