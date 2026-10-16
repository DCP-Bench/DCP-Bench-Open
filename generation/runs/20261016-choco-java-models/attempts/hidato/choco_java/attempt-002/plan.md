Hidato Puzzles start semi-filled with numbered tiles -> puzzle from the instance field (R x C grid, 0 = empty, clue values given)
Fill in the empty cells with the numbers that complete the puzzle -> every cell holds a distinct value 1..R*C (all cells filled), output x[R][C]
Consecutive number must touch horizontally, vertically, or diagonally -> for each v, the cells of v and v+1 are 8-neighbours: table over (pos[v], pos[v+1]) with allowed adjacent flat indices
The numbers must be in increasing order -> the value-to-position map pos[v] is a permutation; consecutive values are placed in order by the chain above
the given numbers stay where they are -> for each clue value v at cell p: pos[v-1] = p
objective: none (satisfaction)
