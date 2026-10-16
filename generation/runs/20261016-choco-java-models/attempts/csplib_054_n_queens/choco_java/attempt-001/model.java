import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// N queens: place n queens on an n x n chessboard so that no two attack each other
// (no two share a row, a column or a diagonal).
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // queens[i] is the column (1..n) of the queen in row i; one queen per row by construction
    IntVar[] queens = m.intVarArray("queens", n, 1, n);

    // no two queens in the same column
    m.allDifferent(queens, "AC").post();

    // no two queens on the same diagonal: shift each column by its row index
    IntVar[] up = new IntVar[n];
    IntVar[] down = new IntVar[n];
    for (int i = 0; i < n; i++) {
      up[i] = m.offset(queens[i], i);
      down[i] = m.offset(queens[i], -i);
    }
    // no two queens on the same diagonal going up
    m.allDifferent(up, "AC").post();
    // no two queens on the same diagonal going down
    m.allDifferent(down, "AC").post();

    out.put("queens", queens);
  }
}
