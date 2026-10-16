The N-Puzzle is a sliding puzzle on a grid of n+1 tiles with one empty tile; the objective is to trace the steps from the start picture to the end picture -> p[s][cell][value] one-hot tile per cell per step, each step a permutation of the tiles
Input includes the start and end state of the puzzle -> unit constraints on step 0 (puzzle_start) and step N_STEPS-1 (puzzle_end)
Start and end states of the puzzle are given -> fixed cells from the instance
The number of steps N_STEPS, including the start and end states -> states s = 0..N_STEPS-1
A move slides one tile into the empty tile, so the empty tile swaps with an adjacent tile -> per step, a tile may only move to an adjacent cell, and only into the cell where the empty tile was
Freezing is not allowed, the state of the puzzle must change at each step -> the empty tile's cell differs between consecutive steps
Print the state of the puzzle at each step (steps) as a list of N_STEPS 2-dimensional matrices -> steps[s][r][c] = sum of value * one-hot bit (integer expression)
satisfaction problem, no objective
