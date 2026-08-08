import json
rows = 8
cols = 13
row_rules = [[0, 1], [0, 2], [4, 4], [0, 12], [0, 8], [0, 9], [3, 4], [2, 2]]
col_rules = [[0, 2], [2, 1], [3, 2], [0, 6], [1, 4], [0, 3], [0, 4], [0, 4], [0, 4], [0, 5], [0, 4], [1, 3], [0, 2]]
def clean(rule):
    return [value for value in rule if value > 0]
def patterns(length, blocks):
    blocks = list(blocks)
    if not blocks:
        return [[0] * length]
    first, rest = blocks[0], blocks[1:]
    min_rest = sum(rest) + len(rest) if rest else 0
    result = []
    for start in range(0, length - first - min_rest + 1):
        prefix = [0] * start + [1] * first
        if rest:
            for tail in patterns(length - start - first - 1, rest):
                result.append(prefix + [0] + tail)
        else:
            result.append(prefix + [0] * (length - start - first))
    return result
def groups(values):
    result = []
    count = 0
    for value in values:
        if value:
            count += 1
        elif count:
            result.append(count)
            count = 0
    if count:
        result.append(count)
    return result
def prefix_ok(values, rule):
    clues = clean(rule)
    completed = []
    active = 0
    for value in values:
        if value:
            active += 1
        elif active:
            completed.append(active)
            active = 0
    for idx, block in enumerate(completed):
        if idx >= len(clues) or block != clues[idx]:
            return False
    if active:
        return len(completed) < len(clues) and active <= clues[len(completed)]
    return len(completed) <= len(clues)
row_patterns = [patterns(cols, clean(rule)) for rule in row_rules]
board = []
def search(row_idx):
    if row_idx == rows:
        return all(groups([board[r][c] for r in range(rows)]) == clean(col_rules[c]) for c in range(cols))
    for pattern in row_patterns[row_idx]:
        board.append(pattern)
        if all(prefix_ok([board[r][c] for r in range(row_idx + 1)], col_rules[c]) for c in range(cols)):
            if search(row_idx + 1):
                return True
        board.pop()
    return False
if not search(0):
    raise RuntimeError('no nonogram solution found')
print(json.dumps({'board': board}))