import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Sudoku: fill the 9x9 grid so that every row, every column and every 3x3 section
// holds the digits 1 to 9, keeping the clues given in the input grid (0 = empty).
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] input = inst.getIntMatrix("input_grid");
    int n = 9;
    IntVar[][] grid = m.intVarMatrix("grid", n, n, 1, n);

    // each row contains all the digits from 1 to 9
    for (int r = 0; r < n; r++) {
      m.allDifferent(grid[r], "AC").post();
    }

    // each column contains all the digits from 1 to 9
    for (int c = 0; c < n; c++) {
      IntVar[] column = new IntVar[n];
      for (int r = 0; r < n; r++) column[r] = grid[r][c];
      m.allDifferent(column, "AC").post();
    }

    // each 3x3 section contains all the digits from 1 to 9
    for (int br = 0; br < n; br += 3) {
      for (int bc = 0; bc < n; bc += 3) {
        IntVar[] section = new IntVar[n];
        for (int k = 0; k < n; k++) section[k] = grid[br + k / 3][bc + k % 3];
        m.allDifferent(section, "AC").post();
      }
    }

    // the filled cells of the input keep their numbers
    for (int r = 0; r < n; r++) {
      for (int c = 0; c < n; c++) {
        if (input[r][c] != 0) m.arithm(grid[r][c], "=", input[r][c]).post();
      }
    }

    out.put("grid", grid);
  }
}
