// Quasigroup completion (CSPLib 067): complete a partially filled order-N Latin square,
// so that every symbol 1..N occurs exactly once in each row and each column.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("N");                       // order of the square
    int[][] start = inst.getIntMatrix("start");     // given cells; 0 marks an empty cell

    // puzzle[i][j]: the symbol in row i, column j
    IntVar[][] puzzle = m.intVarMatrix("cell", n, n, 1, n);

    // every row contains each symbol exactly once
    for (int i = 0; i < n; i++) {
      m.allDifferent(puzzle[i], "AC").post();
    }

    // every column contains each symbol exactly once
    for (int j = 0; j < n; j++) {
      IntVar[] col = new IntVar[n];
      for (int i = 0; i < n; i++) col[i] = puzzle[i][j];
      m.allDifferent(col, "AC").post();
    }

    // the given cells keep their symbols
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        if (start[i][j] != 0) {
          m.arithm(puzzle[i][j], "=", start[i][j]).post();
        }
      }
    }

    out.put("puzzle", puzzle);
  }
}
