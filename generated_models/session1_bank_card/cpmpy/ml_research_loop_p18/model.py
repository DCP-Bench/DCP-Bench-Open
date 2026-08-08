import json
for a in range(1, 10):
    for b in range(10):
        for c in range(10):
            for d in range(10):
                if len({a, b, c, d}) < 4:
                    continue
                if 10 * c + d == 3 * (10 * a + b) and 10 * d + a == 2 * (10 * b + c):
                    print(json.dumps({"a": a, "b": b, "c": c, "d": d}))
                    raise SystemExit
