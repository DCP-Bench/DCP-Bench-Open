"""CSPLib 23, magic hexagon: place the numbers 1 to NUM_CELLS in a hexagon of 19 cells
(rows of 3, 4, 5, 4, 3) so that each of the 15 lines sums to MAGIC_SUM.

      A, B, C
     D, E, F, G
    H, I, J, K, L
     M, N, O, P
      Q, R, S
"""
from docplex.mp.model import Model


def build(instance):
    num_cells = instance["NUM_CELLS"]
    magic_sum = instance["MAGIC_SUM"]
    cells = range(num_cells)
    numbers = range(1, num_cells + 1)

    model = Model("magic_hexagon")

    # holds[c, v] is 1 when cell c holds number v. Every cell holds one number and every
    # number is used exactly once (all different).
    holds = {(c, v): model.binary_var(name=f"holds_{c}_{v}") for c in cells for v in numbers}
    for c in cells:
        model.add_constraint(model.sum(holds[c, v] for v in numbers) == 1)
    for v in numbers:
        model.add_constraint(model.sum(holds[c, v] for c in cells) == 1)

    LD = [model.integer_var(1, num_cells, name=f"LD_{c}") for c in cells]
    for c in cells:
        model.add_constraint(LD[c] == model.sum(v * holds[c, v] for v in numbers))
    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, q, r, s = LD

    # The 15 lines of the hexagon, as the reference lists them, each sum to the magic sum.
    lines = [
        # rows
        [a, b, c], [d, e, f, g], [h, i, j, k, l], [m, n, o, p], [q, r, s],
        # diagonals, top-left to bottom-right
        [a, d, h], [b, e, i, m], [c, f, j, n, q], [g, k, o, r], [l, p, s],
        # diagonals, top-right to bottom-left
        [c, g, l], [b, f, k, p], [a, e, j, o, s], [d, i, n, r], [h, m, q],
    ]
    for line in lines:
        model.add_constraint(model.sum(line) == magic_sum)

    return model, {"LD": LD}
