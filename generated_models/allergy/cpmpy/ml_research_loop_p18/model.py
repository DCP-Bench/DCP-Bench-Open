import itertools
import json
people = range(4)
for baxter, lemon, malone, fleet in itertools.permutations(people):
    if lemon == 2 or fleet == 2 or lemon == 1:
        continue
    for eggs, mold, nuts, ragweed in itertools.permutations(people):
        if mold == 3:
            continue
        if baxter != eggs:
            continue
        if ragweed != 0:
            continue
        if eggs == 1 or mold == 1:
            continue
        print(json.dumps({
            'malone': malone,
            'baxter': baxter,
            'nuts': nuts,
            'ragweed': ragweed,
            'mold': mold,
            'fleet': fleet,
            'lemon': lemon,
            'eggs': eggs,
        }))
        raise SystemExit(0)
raise RuntimeError('no allergy solution found')