import itertools
import json
l = 9
m = (l - 1) // 2
def paf(sequence, shift):
    return sum(sequence[i] * sequence[(i + shift) % l] for i in range(l))
candidates = [seq for seq in itertools.product([-1, 1], repeat=l) if sum(seq) == 1]
for a in candidates:
    for b in candidates:
        if all(paf(a, shift) + paf(b, shift) == -2 for shift in range(1, m + 1)):
            print(json.dumps({'a': list(a), 'b': list(b)}))
            raise SystemExit(0)
raise RuntimeError('no Hadamard Legendre pair found')