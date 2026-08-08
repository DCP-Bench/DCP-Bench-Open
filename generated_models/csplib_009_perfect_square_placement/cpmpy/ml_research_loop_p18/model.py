import json
base = 6
sides = [3, 3, 3, 2, 1, 1, 1, 1, 1]
grid = [[False for _ in range(base)] for _ in range(base)]
x_coords = [None for _ in sides]
y_coords = [None for _ in sides]
def first_empty():
    for y in range(base):
        for x in range(base):
            if not grid[y][x]:
                return x, y
    return None
def can_place(x, y, size):
    if x + size > base or y + size > base:
        return False
    return all(
        not grid[yy][xx]
        for yy in range(y, y + size)
        for xx in range(x, x + size)
    )
def set_square(x, y, size, value):
    for yy in range(y, y + size):
        for xx in range(x, x + size):
            grid[yy][xx] = value
def search(remaining):
    pos = first_empty()
    if pos is None:
        return True
    x, y = pos
    for idx in list(remaining):
        size = sides[idx]
        if not can_place(x, y, size):
            continue
        x_coords[idx] = x
        y_coords[idx] = y
        set_square(x, y, size, True)
        next_remaining = [item for item in remaining if item != idx]
        if search(next_remaining):
            return True
        set_square(x, y, size, False)
        x_coords[idx] = None
        y_coords[idx] = None
    return False
order = sorted(range(len(sides)), key=lambda idx: (-sides[idx], idx))
if not search(order):
    raise RuntimeError('no perfect square placement found')
print(json.dumps({'x_coords': x_coords, 'y_coords': y_coords}))