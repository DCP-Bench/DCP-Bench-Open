import json

total_price = 711
num_items = 4
target_product = total_price * (100 ** (num_items - 1))
for a in range(1, total_price):
    for b in range(a, total_price):
        for c in range(b, total_price):
            d = total_price - a - b - c
            if d < c:
                continue
            if a * b * c * d == target_product:
                print(json.dumps({"prices": [a, b, c, d]}))
                raise SystemExit
