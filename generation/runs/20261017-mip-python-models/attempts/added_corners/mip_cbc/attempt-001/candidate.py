# Added corners: enter the digits 1 through 8 in the circles and squares such that
# the number in each square is equal to the sum of the numbers in the adjoining circles.
# Layout (3x3 grid, centre empty): circles C at the four corners, squares F at the
# four edge midpoints. Outputs are the 8 cells in reading order (left to right, top to bottom).
import mip


def build(instance):
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Cells in reading order, skipping the empty centre:
    # 0 (0,0) C | 1 (0,1) F | 2 (0,2) C | 3 (1,0) F | 4 (1,2) F | 5 (2,0) C | 6 (2,1) F | 7 (2,2) C
    x = [model.add_var(f"p{i}", lb=1, ub=8, var_type=mip.INTEGER) for i in range(8)]

    # Enter the digits 1 through 8 in the circles and squares.
    # Each position takes one value from 1..8 (one-hot binaries), and all eight values differ.
    onehot = [[model.add_var(f"b_{i}_{v}", var_type=mip.BINARY) for v in range(1, 9)] for i in range(8)]
    for i in range(8):
        model.add_constr(mip.xsum(onehot[i]) == 1)
        model.add_constr(x[i] == mip.xsum(v * onehot[i][v - 1] for v in range(1, 9)))
    for v in range(1, 9):
        model.add_constr(mip.xsum(onehot[i][v - 1] for i in range(8)) == 1)

    # Enter the digits 1 through 8 in the circles and squares such that the number in each
    # square is equal to the sum of the numbers in the adjoining circles.
    # Square at the top edge (cell 1) adjoins the top corners 0 and 2.
    model.add_constr(x[1] == x[0] + x[2])
    # Square at the left edge (cell 3) adjoins the left corners 0 and 5.
    model.add_constr(x[3] == x[0] + x[5])
    # Square at the right edge (cell 4) adjoins the right corners 2 and 7.
    model.add_constr(x[4] == x[2] + x[7])
    # Square at the bottom edge (cell 6) adjoins the bottom corners 5 and 7.
    model.add_constr(x[6] == x[5] + x[7])

    return model, {"positions": x}
