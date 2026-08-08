import itertools
import json

num_people = 8
compatible = [
    [2, 3],
    [1, 6],
    [1, 4, 7],
    [2],
    [2],
    [5],
    [8],
    [3],
]
choices = [[0] + donors for donors in compatible]
best = None
for recipients in itertools.product(*choices):
    incoming = [0] * (num_people + 1)
    valid = True
    for donor, recipient in enumerate(recipients, start=1):
        if recipient:
            incoming[recipient] += 1
            if incoming[recipient] > 1:
                valid = False
                break
    if not valid:
        continue
    for person, recipient in enumerate(recipients, start=1):
        if bool(recipient) != bool(incoming[person]):
            valid = False
            break
    if not valid:
        continue
    count = sum(1 for recipient in recipients if recipient)
    if best is None or count > best[0]:
        best = (count, recipients)
matrix = [[0] * num_people for _ in range(num_people)]
for donor, recipient in enumerate(best[1], start=1):
    if recipient:
        matrix[donor - 1][recipient - 1] = 1
print(json.dumps({"transplants": matrix}))
