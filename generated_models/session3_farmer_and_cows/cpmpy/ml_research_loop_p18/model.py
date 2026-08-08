import json

num_cows = 25
quotas = [7, 6, 5, 4, 3]
target = sum(range(1, num_cows + 1)) // len(quotas)
assignment = [-1] * num_cows
counts = [0] * len(quotas)
sums = [0] * len(quotas)
cows = list(range(num_cows, 0, -1))

def search(idx):
    if idx == len(cows):
        return counts == quotas and sums == [target] * len(quotas)
    cow = cows[idx]
    for son in range(len(quotas)):
        if counts[son] >= quotas[son] or sums[son] + cow > target:
            continue
        counts[son] += 1
        sums[son] += cow
        assignment[cow - 1] = son
        if search(idx + 1):
            return True
        assignment[cow - 1] = -1
        sums[son] -= cow
        counts[son] -= 1
    return False

search(0)
print(json.dumps({"cow_assignments": assignment}))
