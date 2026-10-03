# Map colouring: colour the countries so that neighbouring countries differ, using as few colours as
# possible (colours are 1, 2, ...).
from pychoco.model import Model


def build(instance):
    graph = instance["graph"]  # pairs (i, j): country i borders country j, countries numbered from 1
    num_nodes = max(max(edge) for edge in graph)  # the countries are 1..largest number in the graph

    model = Model()

    # colors[i] = the colour of country i+1; with as many colours as countries there is always room
    colors = [model.intvar(1, num_nodes, name=f"colors_{i}") for i in range(num_nodes)]

    # Two neighbouring countries cannot have the same colour.
    for i, j in graph:
        model.arithm(colors[i - 1], "!=", colors[j - 1]).post()

    # Minimise the number of colours used, the largest colour number.
    n_colours = model.intvar(1, num_nodes, name="n_colours")
    model.max(n_colours, colors).post()

    return model, {"colors": colors}, ("minimize", n_colours)
