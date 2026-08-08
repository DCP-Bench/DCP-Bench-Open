import itertools
import json
targets = [16, 17, 23, 24, 39, 40]
best_hits = None
best_key = None
for hits in itertools.product(range(8), repeat=len(targets)):
    score = sum(hit * target for hit, target in zip(hits, targets, strict=True))
    key = (abs(100 - score), sum(hits))
    if best_key is None or key < best_key:
        best_key = key
        best_hits = hits
    if key[0] == 0:
        break
if best_hits is None:
    raise RuntimeError('no archery solution found')
print(json.dumps({'hits': list(best_hits)}))