import itertools
import json

for B, C, F, M, S in itertools.permutations(range(1, 6)):
    if B == 5 or C == 1 or F in {1, 5}:
        continue
    if M <= C:
        continue
    if abs(S - F) == 1 or abs(F - C) == 1:
        continue
    print(json.dumps({"B": B, "C": C, "F": F, "M": M, "S": S}))
    break
