# Category: cube_sudoku_benchmark
# Name: Cube Sudoku
# Source: Patrick Schibli / Dream Factory, Cube Sudoku Benchmark v1.0.0 (CC BY 4.0)
# Source description: https://www.dream-factory.app/cubesudoku/en/datasets
# Problem instances: https://doi.org/10.5281/zenodo.24342566

# Data
givens = [
    0, 6, 1, 3, 0, 0, 0, 0, 0, 4, 0, 9, 1, 0, 2, 0, 0, 0, 8, 3, 2, 0, 5, 9,
    0, 1, 6, 0, 7, 0, 0, 3, 5, 0, 0, 0, 0, 1, 3, 2, 0, 4, 0, 6, 0, 6, 2, 8,
    0, 0, 7, 0, 0, 0, 1, 0, 0, 0, 0, 0, 6, 9, 0, 2, 0, 6, 0, 7, 0, 0, 3, 0,
    0, 4, 5, 0, 0, 0, 7, 0, 1, 0, 0, 0, 0, 0, 0, 7, 0, 3, 0, 0, 6, 0, 0, 5,
    4, 0, 9, 0, 7, 2, 0, 3, 0, 5, 6, 0, 7, 0, 0, 4, 0, 0, 9, 0, 6, 0, 6, 0,
    0, 0, 0, 1, 0, 8, 5, 0, 0, 0, 0, 6, 0, 0, 0, 0, 2, 4, 0, 6, 0, 0, 1, 0,
    0, 3, 0, 0, 5, 1, 0, 0, 0, 6, 0, 0, 9, 4, 8, 0, 0, 7, 9, 0, 0, 0, 4, 6,
    8, 0, 2, 6, 8, 9, 0, 0, 0, 3, 7, 0, 1, 0, 2, 2, 1, 0, 0, 5, 8, 3, 0, 8,
    1, 9, 3, 0, 0, 3, 4, 8, 0, 0, 1, 0, 0, 0, 0, 2, 0, 5, 0, 0, 0, 9, 0, 6,
    0, 0, 0, 9, 5, 1, 0, 0, 0, 7, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 8,
    0, 0, 0, 0, 5, 0, 0, 0, 7, 0, 4, 0, 5, 0, 9, 0, 2, 5, 3, 0, 0, 0, 9, 3,
    0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 0, 0, 3, 0, 6, 3, 0, 0, 6, 0, 8, 9,
    2, 0, 0, 1, 8, 0, 3, 8, 0, 0, 6, 0, 2, 4, 5, 0, 0, 0, 0, 0, 0, 0, 9, 1,
    7, 3, 0, 0, 1, 7, 6, 2, 5, 0, 9, 0, 8, 3, 0, 0, 0, 6, 0, 6, 7, 0, 2, 0,
    0, 1, 6, 9, 2, 0, 0, 0, 2, 0, 6, 3, 4, 0, 8, 0, 0, 0, 5, 0, 6, 7, 0, 2,
    1, 0, 6, 3, 5, 0, 0, 0, 4, 0, 1, 0, 6, 8, 0, 9, 0, 4, 1, 9, 4, 8, 0, 1,
    5, 6,
]
# End of data

import json

import cpmpy as cp


def cube_topology():
    """Return the release's ordered surface coordinates and distinct Sudoku units."""
    index_by_coordinate = {}
    units = set()
    for axis in range(3):
        for boundary in (0, 8):
            face = []
            for row in range(9):
                indices = []
                for column in range(9):
                    point = [column, row]
                    point.insert(axis, boundary)
                    indices.append(index_by_coordinate.setdefault(tuple(point), len(index_by_coordinate)))
                face.append(indices)

            groups = [*face, *zip(*face)]
            for top in range(0, 9, 3):
                for left in range(0, 9, 3):
                    groups.append([cell for row in face[top:top + 3] for cell in row[left:left + 3]])
            units.update(tuple(sorted(group)) for group in groups)
    return tuple(index_by_coordinate), tuple(sorted(units))


def build_model(clues):
    """Build the satisfaction model and its output variables for a 386-cell puzzle."""
    coordinates, units = cube_topology()
    if len(clues) != len(coordinates) or any(type(digit) is not int or not 0 <= digit <= 9 for digit in clues):
        raise ValueError("givens must contain 386 integers from 0 to 9, with 0 marking empty cells")

    cells = cp.intvar(1, 9, shape=len(coordinates), name="cells")
    model = cp.Model([cp.AllDifferent([cells[i] for i in unit]) for unit in units])
    model += [cells[i] == digit for i, digit in enumerate(clues) if digit != 0]
    return model, cells


model, cells = build_model(givens)
model.solve()
solution = {"cells": cells.value().tolist()}
print(json.dumps(solution))
