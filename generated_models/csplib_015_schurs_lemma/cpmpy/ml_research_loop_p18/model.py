import json
n = 13
c = 3
balls = [0 for _ in range(n + 1)]
def valid(up_to):
    for x in range(1, up_to + 1):
        for y in range(1, up_to + 1):
            z = x + y
            if z <= up_to and balls[x] == balls[y] == balls[z]:
                return False
    return True
def search(value):
    if value > n:
        return True
    for colour in range(1, c + 1):
        balls[value] = colour
        if valid(value) and search(value + 1):
            return True
    balls[value] = 0
    return False
if not search(1):
    raise RuntimeError('no Schur colouring found')
print(json.dumps({'balls': balls[1:]}))