"""Map colouring: colour Belgium, Denmark, France, Germany, the Netherlands and Luxembourg so
that neighbouring countries differ, using as few colours as possible.
"""
from docplex.mp.model import Model


def build(instance):
    graph = instance["graph"]  # pairs (i, j) of neighbouring countries, numbered from 1
    # Six countries, as the reference fixes; colours are 1..6, one per country at most.
    num_nodes = 6
    countries = range(num_nodes)
    palette = range(1, num_nodes + 1)

    model = Model("color_simple")

    # paint[i, c] is 1 when country i gets colour c; one colour per country.
    paint = {(i, c): model.binary_var(name=f"country_{i + 1}_colour_{c}") for i in countries
             for c in palette}
    for i in countries:
        model.add_constraint(model.sum(paint[i, c] for c in palette) == 1)
    colors = [model.integer_var(1, num_nodes, name=f"colour_{i + 1}") for i in countries]
    for i in countries:
        model.add_constraint(colors[i] == model.sum(c * paint[i, c] for c in palette))

    # Two neighbouring countries cannot have the same colour.
    for i, j in graph:
        for c in palette:
            model.add_constraint(paint[i - 1, c] + paint[j - 1, c] <= 1)

    # Minimise the number of colours used, the largest colour number.
    used = model.integer_var(1, num_nodes, name="max_colour")
    for i in countries:
        model.add_constraint(used >= colors[i])
    model.minimize(used)

    return model, {"colors": colors}
