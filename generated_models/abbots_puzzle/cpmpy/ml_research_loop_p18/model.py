import json
for men in range(101):
    women = 5 * men
    children = 100 - men - women
    if children < 0:
        continue
    if 6 * men + 4 * women + children == 200:
        print(json.dumps({'men': men, 'women': women, 'children': children}))
        raise SystemExit(0)
raise RuntimeError('no abbots puzzle solution found')