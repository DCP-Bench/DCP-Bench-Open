# Rectangle packing: place n rectangles, given by widths and heights, without overlap
# inside one bounding box, and minimise the area of that box.
from paramita.modelling import Bool, If, Or


def _order_bits(name, size):
    # unary integer in 0..size: bit k is true exactly when the value is at least k + 1
    bits = [Bool(f"{name}_ge_{k}") for k in range(size)]
    # the bits are an order: value >= k + 2 implies value >= k + 1
    return bits, [If(bits[k + 1], bits[k]) for k in range(size - 1)]


def build(instance):
    widths, heights = instance["widths"], instance["heights"]
    n = len(widths)
    items = range(n)
    # the box cannot be wider or taller than all items placed side by side
    SX, SY = sum(widths), sum(heights)

    cons = []

    # the box width total_x and height total_y, each as unary order bits
    gx, cx = _order_bits("total_x", SX)
    gy, cy = _order_bits("total_y", SY)
    cons += cx + cy
    total_x = sum(gx)
    total_y = sum(gy)

    # the box is at least as wide as the widest item and as tall as the tallest item
    cons += [gx[k] for k in range(max(widths))]
    cons += [gy[k] for k in range(max(heights))]

    # the lower-left corner of each item, as unary order bits (value 0 .. box size - 1)
    px, py = [], []
    for i in items:
        bx, c1 = _order_bits(f"pos_x_{i}", SX)
        by, c2 = _order_bits(f"pos_y_{i}", SY)
        cons += c1 + c2
        px.append(bx)
        py.append(by)
    pos_x = [sum(px[i]) for i in items]
    pos_y = [sum(py[i]) for i in items]

    # every item lies inside the box: its corner plus its size stays within total_x and total_y
    for i in items:
        cons.append(pos_x[i] + widths[i] <= total_x)
        cons.append(pos_y[i] + heights[i] <= total_y)

    # no two items overlap: for each pair one of the four sides separates them
    for i in items:
        for j in range(i + 1, n):
            left = Bool(f"left_{i}_{j}")       # item i lies left of item j
            right = Bool(f"right_{i}_{j}")     # item j lies left of item i
            below = Bool(f"below_{i}_{j}")     # item i lies below item j
            above = Bool(f"above_{i}_{j}")     # item j lies below item i
            cons.append(Or([left, right, below, above]))
            cons.append(If(left, pos_x[i] + widths[i] <= pos_x[j]))
            cons.append(If(right, pos_x[j] + widths[j] <= pos_x[i]))
            cons.append(If(below, pos_y[i] + heights[i] <= pos_y[j]))
            cons.append(If(above, pos_y[j] + heights[j] <= pos_y[i]))

    # the area total_x * total_y is the number of cells (a, b) with a <= total_x and b <= total_y.
    # cell[a][b] is forced on when both bounds reach a and b; minimising counts exactly the area.
    cell = [[Bool(f"cell_{a}_{b}") for b in range(SY)] for a in range(SX)]
    for a in range(SX):
        for b in range(SY):
            cons.append(If(gx[a] & gy[b], cell[a][b]))
    # each row is summed on its own, then the rows are added: a single flat sum of
    # every cell nests too deeply for the runner's expression walk
    area = sum(sum(row) for row in cell)

    return cons, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}, ("minimize", area)
