Fill the surface of a cube with digits from 1 to 9. The cube has six 9-by-9 Sudoku faces. Every row, column and 3-by-3 box of each face must contain every digit from 1 to 9 exactly once. Boxes start at row and column indices 0, 3 and 6. An edge cell belongs to two faces and a corner cell belongs to three. Each physical cell holds one digit shared by all faces that contain it.

The input `givens` is a string of 386 digits. A `0` denotes an empty cell and a digit from `1` to `9` fixes the value of that cell. Number the cells by visiting the following faces in order, scanning each face row by row from index 0 to 8. Within each row, scan columns from index 0 to 8. Assign the next zero-based index when a coordinate is first visited. Reuse that index whenever the same coordinate is visited again.

| Face | Coordinate of row `r`, column `c` |
| --- | --- |
| `x = 0` | `(0, c, r)` |
| `x = 8` | `(8, c, r)` |
| `y = 0` | `(c, 0, r)` |
| `y = 8` | `(c, 8, r)` |
| `z = 0` | `(c, r, 0)` |
| `z = 8` | `(c, r, 8)` |

The character at index `i` in `givens` refers to the physical cell with index `i` in this traversal. Find a complete assignment that preserves every clue and satisfies every face.

Print the 386 cell values (cells) as a list of integers from 1 to 9 in this index order.
