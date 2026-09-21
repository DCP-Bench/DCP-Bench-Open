# Colour adjacent countries differently, using as few colours as possible.
from dcp_pb import Pb


def build(instance):
    graph = instance["graph"]
    # The edge list numbers the countries 1..num_nodes.
    num_nodes = max(max(edge) for edge in graph)

    pb = Pb()
    colors = pb.ints(num_nodes, 1, num_nodes)
    for left, right in graph:
        pb.different(colors[left - 1], colors[right - 1])

    # Minimising an upper bound on every colour drives it to the largest one.
    used = pb.int(1, num_nodes)
    for colour in colors:
        pb.le([(1, colour), (-1, used)], 0)
    pb.minimise([(1, used)])
    return pb, {"colors": colors}
