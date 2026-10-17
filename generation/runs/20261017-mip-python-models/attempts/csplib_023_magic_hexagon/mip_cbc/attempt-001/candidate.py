# Magic hexagon (csplib 023): place the numbers 1..NUM_CELLS in the 19 cells A..S
# of a hexagonal grid (rows A B C / D E F G / H I J K L / M N O P / Q R S) so that
# each of the 15 lines (rows and diagonals) sums to MAGIC_SUM. Output LD lists the
# values of A..S in order.
import mip


# Cell order: A B C D E F G H I J K L M N O P Q R S -> indices 0..18
LINES = [
    # rows
    [0, 1, 2],
    [3, 4, 5, 6],
    [7, 8, 9, 10, 11],
    [12, 13, 14, 15],
    [16, 17, 18],
    # diagonals going down-right
    [0, 4, 9, 14, 18],
    [1, 5, 10, 15],
    [2, 6, 11],
    [3, 8, 13, 17],
    [7, 12, 16],
    # diagonals going down-left
    [2, 5, 9, 13, 16],
    [1, 4, 8, 12],
    [0, 3, 7],
    [6, 10, 14, 17],
    [11, 15, 18],
]


def build(instance):
    n = instance["NUM_CELLS"]
    magic = instance["MAGIC_SUM"]
    cells = 19

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
    # This is a feasibility question (no objective): ask CBC to favour finding a solution
    model.emphasis = 1

    x = [model.add_var(f"x_{i}", lb=1, ub=n, var_type=mip.INTEGER) for i in range(cells)]

    # The numbers 1 to NUM_CELLS are all different: for each pair of cells, one is below the
    # other (binary b: b = 1 means cell i is above cell j, otherwise cell j is above cell i)
    for i in range(cells):
        for j in range(i + 1, cells):
            b = model.add_var(f"b_{i}_{j}", var_type=mip.BINARY)
            model.add_constr(x[i] - x[j] >= 1 - n * (1 - b))
            model.add_constr(x[j] - x[i] >= 1 - n * b)

    # Each of the 15 lines (rows and diagonals) sums to the magic constant
    for line in LINES:
        model.add_constr(mip.xsum(x[i] for i in line) == magic)

    return model, {"LD": x}
