import json
at_most = [1, 2, 2, 2, 1]
per_slots = [2, 3, 3, 5, 5]
demand = [1, 1, 2, 2, 2, 2]
requires = [[1, 0, 1, 1, 0], [0, 0, 0, 1, 0], [0, 1, 0, 0, 1], [0, 1, 0, 1, 0], [1, 0, 1, 0, 0], [1, 1, 0, 0, 0]]
n_cars = sum(demand)
n_options = len(at_most)
def prefix_ok(seq):
    for option in range(n_options):
        window = per_slots[option]
        cap = at_most[option]
        start = max(0, len(seq) - window)
        while start + window <= len(seq):
            used = sum(requires[seq[i]][option] for i in range(start, start + window))
            if used > cap:
                return False
            start += 1
    return True
def solve(seq, remaining):
    if len(seq) == n_cars:
        return seq
    for car_type, count in enumerate(remaining):
        if count <= 0:
            continue
        candidate = seq + [car_type]
        if not prefix_ok(candidate):
            continue
        next_remaining = list(remaining)
        next_remaining[car_type] -= 1
        result = solve(candidate, next_remaining)
        if result is not None:
            return result
    return None
sequence = solve([], list(demand))
if sequence is None:
    raise RuntimeError('no car sequence found')
print(json.dumps({'sequence': sequence}))