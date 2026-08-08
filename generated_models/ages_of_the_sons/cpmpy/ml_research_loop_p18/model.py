import json
products = []
for a1 in range(1, 37):
    for a2 in range(1, a1 + 1):
        for a3 in range(1, a2 + 1):
            if a1 * a2 * a3 == 36:
                products.append((a1 + a2 + a3, a1, a2, a3))
ambiguous_sums = {total for total, *_ in products if sum(1 for item in products if item[0] == total) > 1}
for total, a1, a2, a3 in products:
    if total in ambiguous_sums and a1 > a2:
        print(json.dumps({'A1': a1, 'A2': a2, 'A3': a3}))
        raise SystemExit(0)
raise RuntimeError('no ages of the sons solution found')