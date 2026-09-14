import cpmpy as cp


def build(instance):
    n, c = instance["n"], instance["c"]
    balls = cp.intvar(1, c, shape=n, name="balls")
    model = cp.Model()
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            if z <= n:
                model += ((balls[x - 1] != balls[y - 1])
                          | (balls[x - 1] != balls[z - 1])
                          | (balls[y - 1] != balls[z - 1]))
    return model, {"balls": [balls[i] for i in range(n)]}
