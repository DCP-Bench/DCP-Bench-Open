// A knight's tour on an n x n chessboard: the knight visits every square exactly once,
// and the move numbers x[r][c] run from 0 to n*n-1 (the tour does not need to return to its start).
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int cells = n * n;

    // the move number of each square, from 0 to n*n-1
    CPIntVar[][] x = new CPIntVar[n][n];
    CPIntVar[] flat = new CPIntVar[cells];
    for (int r = 0; r < n; r++) {
      for (int c = 0; c < n; c++) {
        x[r][c] = m.intVar(0, cells - 1);
        flat[r * n + c] = x[r][c];
      }
    }

    // the knight visits every square exactly once: all move numbers are different
    m.cp().post(allDifferent(flat));

    // each move is a knight's move: when square b is visited right after square a,
    // b must be a knight's move away from a. Pairs that are not a knight's move apart
    // therefore never have move numbers that differ by one.
    for (int a = 0; a < cells; a++) {
      int ar = a / n, ac = a % n;
      for (int b = 0; b < cells; b++) {
        if (a == b) continue;
        int br = b / n, bc = b % n;
        int dr = Math.abs(ar - br), dc = Math.abs(ac - bc);
        boolean knightMove = (dr == 1 && dc == 2) || (dr == 2 && dc == 1);
        if (!knightMove) {
          // square b is not reached right after square a
          m.cp().post(neq(flat[b], plus(flat[a], 1)));
        }
      }
    }

    out.put("x", x);
  }
}
