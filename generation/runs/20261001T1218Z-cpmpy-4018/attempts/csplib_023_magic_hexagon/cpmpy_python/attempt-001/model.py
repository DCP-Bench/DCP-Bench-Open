# CSPLib prob023, magic hexagon: place the numbers 1..19 (each once) in the cells of a hexagon with
# rows of 3, 4, 5, 4 and 3 cells so that every straight line of cells sums to the magic constant.
import cpmpy as cp


def build(instance):
    num_cells = instance["NUM_CELLS"]
    magic_sum = instance["MAGIC_SUM"]

    # The hexagon has side k when it has 3k(k-1)+1 cells (k = 3 gives the 19 cells of the problem).
    k = 1
    while 3 * k * (k - 1) + 1 < num_cells:
        k += 1

    # Row lengths from top to bottom: k, k+1, ..., 2k-1, ..., k+1, k.
    row_lengths = list(range(k, 2 * k)) + list(range(2 * k - 2, k - 1, -1))

    # Cells are numbered row by row, left to right. A cell is placed at a horizontal position x
    # (neighbouring cells of a row are 2 apart, and a row below is shifted by 1), which lets us
    # read off the three kinds of straight lines:
    #   - cells of the same row,
    #   - cells with the same x + row  (diagonal going down-left),
    #   - cells with the same x - row  (diagonal going down-right).
    rows, down_left, down_right = {}, {}, {}
    cell = 0
    for r, length in enumerate(row_lengths):
        start = (2 * k - 1) - length  # shorter rows start further right
        for i in range(length):
            x = start + 2 * i
            rows.setdefault(r, []).append(cell)
            down_left.setdefault(x + r, []).append(cell)
            down_right.setdefault(x - r, []).append(cell)
            cell += 1
    lines = list(rows.values()) + list(down_left.values()) + list(down_right.values())

    # LD[c] = number placed in cell c
    LD = cp.intvar(1, num_cells, shape=(num_cells,), name="LD")

    model = cp.Model()

    # Every number from 1 to NUM_CELLS is used exactly once.
    model += cp.AllDifferent(LD)

    # The numbers along each straight line of cells (rows and both diagonal directions) add up to
    # the magic constant.
    for line in lines:
        model += cp.sum([LD[c] for c in line]) == magic_sum

    return model, {"LD": LD}
