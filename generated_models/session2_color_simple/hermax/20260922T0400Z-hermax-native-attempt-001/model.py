# Colour adjacent countries differently, using as few colours as possible.
from hermax.model import Model


def build(instance):
    graph = instance["graph"]
    # The edge list numbers the countries 1..num_nodes.
    num_nodes = max(max(edge) for edge in graph)

    m = Model()
    colors = m.int_vector("colors", num_nodes, 1, num_nodes)
    for left, right in graph:
        m &= (colors[left - 1] != colors[right - 1])

    # Minimising the largest colour used drives the palette down.
    m.obj += m.max(colors, name="used")
    return m, {"colors": colors}
