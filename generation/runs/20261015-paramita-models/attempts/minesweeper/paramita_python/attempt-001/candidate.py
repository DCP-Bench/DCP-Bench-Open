"""Minesweeper: decide which unopened cells hold a mine, given the numbered clues.

A numbered cell is open, so it holds no mine. The number on a numbered cell is the
count of mines among its neighbours (up to eight adjacent cells). Unopened cells
carry the marker X and have no clue of their own.
"""
from paramita.modelling import Bool


def build(instance):
    X = instance["X"]  # marker for an unopened cell, read from the instance
    board = instance["game_data"]
    rows, cols = len(board), len(board[0])

    # one Bool per cell: mine[r][c] is true when the cell holds a mine
    mine = [[Bool(f"mine_{r}_{c}") for c in range(cols)] for r in range(rows)]

    cons = []
    # an open cell (one showing a number) is not a mine
    for r in range(rows):
        for c in range(cols):
            if board[r][c] != X:
                cons.append(~mine[r][c])

    # the number on an open cell is the count of mines in the adjacent cells
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == X:
                continue
            neighbours = [
                mine[rr][cc]
                for rr in range(r - 1, r + 2)
                for cc in range(c - 1, c + 2)
                if (rr, cc) != (r, c) and 0 <= rr < rows and 0 <= cc < cols
            ]
            cons.append(sum(neighbours) == board[r][c])

    outputs = {"mines": [[mine[r][c] for c in range(cols)] for r in range(rows)]}
    return cons, outputs
