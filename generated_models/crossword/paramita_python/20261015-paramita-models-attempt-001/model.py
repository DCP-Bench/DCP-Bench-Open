# Crossword: fill a 6x5 grid (# = black cell) with 8 words from a list of 15.
# The grid is numbered; the words start at locations 1..8.
# Words are numbered 0..14 in the order: length descending, then alphabetical.
# Encoding: one-hot Bool per (slot, word) choice; each slot takes exactly one word.
from paramita.modelling import Bool

# The grid and word list are the problem's own data (the statement fixes them, the
# instance is empty), so they are written here. Digits mark numbered cells, '#' black cells.
GRID = [
    "1.2.3",
    "##.#.",
    "#4.5.",
    "6#7..",
    "8....",
    ".##.#",
]

WORDS = [
    "HOSES", "LASER", "SAILS", "SHEET", "STEER",
    "HEEL", "HIKE", "KEEL", "KNOT", "LINE",
    "AFT", "ALE", "EEL", "LEE", "TIE",
]


def find_slots(grid):
    """Across and down word slots. A slot is a run of two or more white cells."""
    rows, cols = len(grid), len(grid[0])
    slots = []
    for r in range(rows):
        c = 0
        while c < cols:
            if grid[r][c] == "#":
                c += 1
                continue
            start = c
            while c < cols and grid[r][c] != "#":
                c += 1
            if c - start >= 2:
                slots.append({"number": int(grid[r][start]) if grid[r][start].isdigit() else None,
                              "cells": [(r, k) for k in range(start, c)]})
    for c in range(cols):
        r = 0
        while r < rows:
            if grid[r][c] == "#":
                r += 1
                continue
            start = r
            while r < rows and grid[r][c] != "#":
                r += 1
            if r - start >= 2:
                slots.append({"number": int(grid[start][c]) if grid[start][c].isdigit() else None,
                              "cells": [(k, c) for k in range(start, r)]})
    return slots


def build(instance):
    slots = find_slots(GRID)
    # the numbered slots are 1..8; order the slots by their starting number
    slots.sort(key=lambda s: s["number"])
    assert len(slots) == 8 and all(s["number"] is not None for s in slots)
    n_words = len(WORDS)

    # w[k][j]: word j fills slot k
    w = [[Bool(f"w_{k}_{j}") for j in range(n_words)] for k in range(len(slots))]
    cons = []

    # each slot holds exactly one word, of its own length
    for k, slot in enumerate(slots):
        cons.append(sum(w[k]) == 1)
        for j, word in enumerate(WORDS):
            if len(word) != len(slot["cells"]):
                cons.append(~w[k][j])

    # the eight selected words are distinct: each word fills at most one slot
    for j in range(n_words):
        cons.append(sum(w[k][j] for k in range(len(slots))) <= 1)

    # a letter shared by an across and a down word must be the same letter in both
    cell_owner = {}
    for k, slot in enumerate(slots):
        for pos, cell in enumerate(slot["cells"]):
            cell_owner.setdefault(cell, []).append((k, pos))
    for cell, owners in cell_owner.items():
        if len(owners) < 2:
            continue
        (a, i), (b, jpos) = owners
        for u, wu in enumerate(WORDS):
            if i >= len(wu):
                continue
            for v, wv in enumerate(WORDS):
                if jpos >= len(wv):
                    continue
                if wu[i] != wv[jpos]:
                    cons.append(~(w[a][u] & w[b][v]))

    # E[k]: index of the word in the slot numbered k+1
    E = [sum(j * w[k][j] for j in range(n_words)) for k in range(len(slots))]
    return cons, {"E": E}
