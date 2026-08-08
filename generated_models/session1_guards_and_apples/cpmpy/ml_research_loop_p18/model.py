import json
num_gates = 5
after = 1
values = [after]
for _ in range(num_gates):
    before = 2 * (after + 1)
    values.append(before)
    after = before
print(json.dumps({"apples": list(reversed(values))}))
