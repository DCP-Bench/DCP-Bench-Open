import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Sudoku: fill a 9x9 grid with the digits 1 to 9 so that each row, each column
// and each 3x3 section contains all the digits. The input grid has some cells
// filled (0 means empty); the solved grid is the output.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] input = inst.getIntMatrix("input_grid");
    int n = 9;

    // the grid: one variable per cell, each a digit from 1 to 9
    CPIntVar[][] grid = new CPIntVar[n][n];
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        grid[i][j] = m.intVar(1, 9);
      }
    }

    // the filled cells keep the digit given in the input
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        if (input[i][j] != 0) {
          m.cp().post(eq(grid[i][j], input[i][j]));
        }
      }
    }

    // each row contains all the digits between 1 and 9
    for (int i = 0; i < n; i++) {
      m.cp().post(allDifferent(grid[i]));
    }

    // each column contains all the digits between 1 and 9
    for (int j = 0; j < n; j++) {
      CPIntVar[] col = new CPIntVar[n];
      for (int i = 0; i < n; i++) {
        col[i] = grid[i][j];
      }
      m.cp().post(allDifferent(col));
    }

    // each 3x3 section contains all the digits between 1 and 9
    for (int bi = 0; bi < 3; bi++) {
      for (int bj = 0; bj < 3; bj++) {
        CPIntVar[] section = new CPIntVar[n];
        int k = 0;
        for (int i = 0; i < 3; i++) {
          for (int j = 0; j < 3; j++) {
            section[k++] = grid[3 * bi + i][3 * bj + j];
          }
        }
        m.cp().post(allDifferent(section));
      }
    }

    out.put("grid", grid);
  }
}
