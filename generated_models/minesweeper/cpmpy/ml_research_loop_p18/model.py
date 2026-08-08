import json

X = -1
game_data = [
    [2, 3, X, 2, 2, X, 2, 1],
    [X, X, 4, X, X, 4, X, 2],
    [X, X, X, X, X, X, 4, X],
    [X, 5, X, 6, X, X, X, 2],
    [2, X, X, X, 5, 5, X, 2],
    [1, 3, 4, X, X, X, 4, X],
    [0, 1, X, 4, X, X, X, 3],
    [0, 1, 2, X, 2, 3, X, 2],
]
rows, cols = len(game_data), len(game_data[0])
unknowns = [(r, c) for r in range(rows) for c in range(cols) if game_data[r][c] == X]
mines = [[False if game_data[r][c] != X else None for c in range(cols)] for r in range(rows)]
clues = [(r, c, game_data[r][c]) for r in range(rows) for c in range(cols) if game_data[r][c] != X]

def neighbors(r, c):
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                yield nr, nc

def valid_partial():
    for r, c, clue in clues:
        assigned = 0
        possible = 0
        for nr, nc in neighbors(r, c):
            value = mines[nr][nc]
            if value is True:
                assigned += 1
            elif value is None:
                possible += 1
        if assigned > clue or assigned + possible < clue:
            return False
    return True

def search(idx):
    if idx == len(unknowns):
        return all(
            sum(1 for nr, nc in neighbors(r, c) if mines[nr][nc]) == clue
            for r, c, clue in clues
        )
    r, c = unknowns[idx]
    for value in [False, True]:
        mines[r][c] = value
        if valid_partial() and search(idx + 1):
            return True
    mines[r][c] = None
    return False

search(0)
print(json.dumps({"mines": mines}))
