import itertools
import json
fixed = {'A': 16, 'B': 2, 'F': 8, 'G': 14}
available = set(range(1, 100)) - set(fixed.values())
for C, H in itertools.permutations(available, 2):
    if fixed['B'] ** 2 + C ** 2 != fixed['G'] ** 2 + H ** 2:
        continue
    for D, I in itertools.permutations(available - {C, H}, 2):
        if C ** 2 + D ** 2 != H ** 2 + I ** 2:
            continue
        for E, K in itertools.permutations(available - {C, H, D, I}, 2):
            if D ** 2 + E ** 2 != I ** 2 + K ** 2:
                continue
            if E ** 2 + fixed['F'] ** 2 != K ** 2 + fixed['A'] ** 2:
                continue
            print(json.dumps({
                'A': fixed['A'], 'B': fixed['B'], 'C': C, 'D': D, 'E': E,
                'F': fixed['F'], 'G': fixed['G'], 'H': H, 'I': I, 'K': K,
            }))
            raise SystemExit(0)
raise RuntimeError('no circling squares solution found')