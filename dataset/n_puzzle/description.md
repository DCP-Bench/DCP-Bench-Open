The N-Puzzle is a classic sliding puzzle game where the goal is to move tiles on a grid to achieve a specific end
configuration. The puzzle consists of a grid with \( n+1 \) tiles, one of which is empty. The objective is to trace
the steps to the original picture by moving the tiles into their correct positions.

Input includes the start and end state of the puzzle, in which 0 is the empty tile, along with the number of steps to the solution, which includes the start and end states.
Each step moves one tile that is horizontally or vertically next to the empty tile into the empty position.
Also, "freezing" is not allowed, meaning that the state of the puzzle must change at each step.

Print the state of the puzzle at each step (steps) as a list of exactly N_STEPS integer 2-dimensional matrices, including the start and end states.
