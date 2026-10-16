import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Futoshiki: fill an n x n grid with the digits 1 to n so that every row and every
// column contains each digit once, the given digits are kept, and every
// inequality between neighbouring squares holds.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] values = inst.getIntMatrix("values");   // 0 = empty square, otherwise the given digit
    int[][] lt = inst.getIntMatrix("lt");           // [r1, c1, r2, c2], 1-based: square 1 is lower than square 2
    int n = values.length;

    // the grid, each square holds a digit from 1 to n
    IntVar[][] grid = m.intVarMatrix("grid", n, n, 1, n);

    // every row contains each of the digits 1 to n once
    for (int r = 0; r < n; r++) {
      m.allDifferent(grid[r], "AC").post();
    }

    // every column contains each of the digits 1 to n once
    for (int c = 0; c < n; c++) {
      IntVar[] col = new IntVar[n];
      for (int r = 0; r < n; r++) col[r] = grid[r][c];
      m.allDifferent(col, "AC").post();
    }

    // some digits are given at the start
    for (int r = 0; r < n; r++) {
      for (int c = 0; c < n; c++) {
        if (values[r][c] != 0) grid[r][c].eq(values[r][c]).post();
      }
    }

    // one square must be lower than its neighbour (inequality clues)
    for (int[] clue : lt) {
      IntVar lower = grid[clue[0] - 1][clue[1] - 1];
      IntVar higher = grid[clue[2] - 1][clue[3] - 1];
      m.arithm(lower, "<", higher).post();
    }

    // branch on the squares, fewest remaining digits first
    IntVar[] cells = new IntVar[n * n];
    for (int r = 0; r < n; r++) {
      for (int c = 0; c < n; c++) cells[r * n + c] = grid[r][c];
    }
    m.getSolver().setSearch(Search.minDomLBSearch(cells));

    out.put("grid", grid);
  }
}
