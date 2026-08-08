import itertools
import json
for positions in itertools.permutations(range(1, 9)):
    if (
        positions[1] == positions[0] + positions[2]
        and positions[3] == positions[0] + positions[5]
        and positions[4] == positions[2] + positions[7]
        and positions[6] == positions[5] + positions[7]
    ):
        print(json.dumps({'positions': list(positions)}))
        raise SystemExit(0)
raise RuntimeError('no added corners solution found')