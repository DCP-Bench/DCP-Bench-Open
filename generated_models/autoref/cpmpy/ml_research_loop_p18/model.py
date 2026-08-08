import json
from cpmpy import *
n = 27
m = 5
s = intvar(0, n + 2, shape=n + 2, name='s')
model = Model([s[n + 1] == m])
for value in range(n + 1):
    model += s[value] == sum(s[idx] == value for idx in range(n + 2))
if not model.solve():
    raise RuntimeError('no autoref solution found')
print(json.dumps({'s': s.value().tolist()}))