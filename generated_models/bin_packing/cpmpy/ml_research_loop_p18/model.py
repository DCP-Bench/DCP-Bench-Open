import json
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
bins = [None for _ in weights]
loads = [0 for _ in range(num_bins)]
def search(item):
    if item == len(weights):
        return True
    for bin_id in range(num_bins):
        if loads[bin_id] + weights[item] > capacity:
            continue
        bins[item] = bin_id
        loads[bin_id] += weights[item]
        if search(item + 1):
            return True
        loads[bin_id] -= weights[item]
        bins[item] = None
    return False
if not search(0):
    raise RuntimeError('no bin packing solution found')
print(json.dumps({'bins': bins}))