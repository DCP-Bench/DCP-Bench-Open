# Crossword: complete the 6 x 5 grid (6 rows, 5 columns, '#' is a black cell) by
# selecting 8 words from the list of 15 so that every across and down word can be
# written into the grid. Output E[k] is the 0-based index of the word that starts at
# location k+1 (locations numbered in reading order), with the words sorted longest
# first and then alphabetically.
import mip

GRID = [
    ".....",
    "##.#.",
    "#....",
    ".#...",
    ".....",
    ".##.#",
]

WORDS = sorted(
    ["AFT", "ALE", "EEL", "HEEL", "HIKE", "HOSES", "KEEL", "KNOT", "LASER", "LEE",
     "LINE", "SAILS", "SHEET", "STEER", "TIE"],
    key=lambda w: (-len(w), w),
)


def build(instance):
    rows, cols = len(GRID), len(GRID[0])

    def white(r, c):
        return 0 <= r < rows and 0 <= c < cols and GRID[r][c] == "."

    # The slots are the across and down runs of two or more white cells, listed in
    # reading order of their first cell. Their numbers are the location numbers.
    slots = []
    for r in range(rows):
        for c in range(cols):
            if not white(r, c):
                continue
            if not white(r, c - 1) and white(r, c + 1):
                cells = []
                k = c
                while white(r, k):
                    cells.append((r, k))
                    k += 1
                slots.append(cells)
            if not white(r - 1, c) and white(r + 1, c):
                cells = []
                k = r
                while white(k, c):
                    cells.append((k, c))
                    k += 1
                slots.append(cells)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Select one word for each slot. x[s][w] is 1 when slot s takes word w, and only
    # words of the slot's length are offered.
    x = []
    for s, cells in enumerate(slots):
        x.append({
            w: model.add_var(f"x_{s}_{w}", var_type=mip.BINARY)
            for w, word in enumerate(WORDS) if len(word) == len(cells)
        })

    # Select 8 words from the list of 15: each slot takes exactly one word.
    for s in range(len(slots)):
        model.add_constr(mip.xsum(x[s].values()) == 1)

    # Each word of the list is used at most once.
    for w in range(len(WORDS)):
        terms = [x[s][w] for s in range(len(slots)) if w in x[s]]
        if terms:
            model.add_constr(mip.xsum(terms) <= 1)

    # The crossword puzzle can be completed: where an across and a down word share a
    # cell, the two words have the same letter there. For each letter, the chosen words
    # of both slots have that letter at the shared position, or neither does.
    uses_of = {}
    for s, cells in enumerate(slots):
        for p, cell in enumerate(cells):
            uses_of.setdefault(cell, []).append((s, p))
    letters = sorted(set("".join(WORDS)))
    for uses in uses_of.values():
        if len(uses) < 2:
            continue
        s1, p1 = uses[0]
        for s2, p2 in uses[1:]:
            for letter in letters:
                lhs = [x[s1][w] for w in x[s1] if WORDS[w][p1] == letter]
                rhs = [x[s2][w] for w in x[s2] if WORDS[w][p2] == letter]
                if not lhs and not rhs:
                    continue
                model.add_constr(mip.xsum(lhs) - mip.xsum(rhs) == 0)

    # E[k] is the index of the word chosen for slot k, an integer tied to the choice.
    E = []
    for s in range(len(slots)):
        e = model.add_var(f"E_{s}", lb=0, ub=len(WORDS) - 1, var_type=mip.INTEGER)
        model.add_constr(e - mip.xsum(w * v for w, v in x[s].items()) == 0)
        E.append(e)

    return model, {"E": E}
