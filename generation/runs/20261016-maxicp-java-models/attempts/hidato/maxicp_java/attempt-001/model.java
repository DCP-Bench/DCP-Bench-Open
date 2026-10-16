import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Hidato: fill a rectangular grid with the numbers 1..R*C, each used once,
// so that consecutive numbers touch horizontally, vertically or diagonally.
// Some cells are given; a 0 in the puzzle is an empty cell.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] puzzle = inst.getIntMatrix("puzzle");
    int rows = puzzle.length;
    int cols = puzzle[0].length;
    int n = rows * cols;

    // every cell holds a number from 1 to the number of cells
    CPIntVar[][] x = new CPIntVar[rows][cols];
    CPIntVar[] cells = new CPIntVar[n];
    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) {
        x[r][c] = m.intVar(1, n);
        cells[r * cols + c] = x[r][c];
      }
    }

    // the numbers 1 to n are each used exactly once
    m.cp().post(allDifferent(cells));

    // the given numbers keep their cells
    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) {
        if (puzzle[r][c] != 0) {
          m.cp().post(eq(x[r][c], puzzle[r][c]));
        }
      }
    }

    // consecutive numbers touch: if a cell holds k (k < n), one of its
    // neighbours holds k + 1
    for (int r = 0; r < rows; r++) {
      for (int c = 0; c < cols; c++) {
        for (int k = 1; k < n; k++) {
          CPBoolVar[] clause = new CPBoolVar[9];
          int size = 0;
          clause[size++] = not(isEq(x[r][c], k));
          for (int dr = -1; dr <= 1; dr++) {
            for (int dc = -1; dc <= 1; dc++) {
              if (dr == 0 && dc == 0) continue;
              int nr = r + dr;
              int nc = c + dc;
              if (nr < 0 || nr >= rows || nc < 0 || nc >= cols) continue;
              clause[size++] = isEq(x[nr][nc], k + 1);
            }
          }
          CPBoolVar[] used = new CPBoolVar[size];
          System.arraycopy(clause, 0, used, 0, size);
          m.cp().post(or(used));
        }
      }
    }

    out.put("x", x);
  }
}
