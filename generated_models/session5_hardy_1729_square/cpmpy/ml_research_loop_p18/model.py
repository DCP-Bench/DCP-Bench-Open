import itertools
import json

for a, b, c, d in itertools.permutations(range(1, 101), 4):
    if a * a + b * b == c * c + d * d:
        print(json.dumps({"a": a, "b": b, "c": c, "d": d}))
        break
