import itertools
import json
m = [[1, 1, 1, 1], [0, 1, 1, 0], [1, 0, 0, 1], [1, 0, 0, 1]]
for assigned_slots in itertools.permutations(range(4)):
    if all(m[person][assigned_slots[person]] for person in range(4)):
        x = [[1 if assigned_slots[person] == slot else 0 for slot in range(4)] for person in range(4)]
        print(json.dumps({'x': x}))
        raise SystemExit(0)
raise RuntimeError('no appointment schedule found')