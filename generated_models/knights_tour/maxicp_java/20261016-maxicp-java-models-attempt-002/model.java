// A knight's tour on an n x n chessboard: the knight visits every square exactly once,
// and the move number x[r][c] of each square runs from 0 to n*n-1.
// The tour does not return to its start, and the start square is free.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.List;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int cells = n * n;

    // knight's moves: square a to square b is one knight's move apart
    List<int[]> moves = new ArrayList<>();
    for (int a = 0; a < cells; a++) {
      for (int b = 0; b < cells; b++) {
        int dr = Math.abs(a / n - b / n), dc = Math.abs(a % n - b % n);
        if ((dr == 1 && dc == 2) || (dr == 2 && dc == 1)) moves.add(new int[]{a, b});
      }
    }
    int[][] knightRows = moves.toArray(new int[0][]);

    // the square visited at each move number k, as a flat index r*n+c
    CPIntVar[] visit = m.intVarArray(cells, 0, cells - 1);

    // the knight visits every square exactly once
    m.cp().post(allDifferent(visit));

    // each move goes from the square of move k to a square one knight's move away, for move k+1
    for (int k = 0; k + 1 < cells; k++) {
      m.cp().post(table(new CPIntVar[]{visit[k], visit[k + 1]}, knightRows));
    }

    // the output: the move number of each square, the inverse of visit
    CPIntVar[][] x = new CPIntVar[n][n];
    for (int r = 0; r < n; r++) {
      for (int c = 0; c < n; c++) {
        x[r][c] = m.intVar(0, cells - 1);
      }
    }

    // square i has move number k exactly when visit[k] is square i
    for (int i = 0; i < cells; i++) {
      CPIntVar xi = x[i / n][i % n];
      for (int k = 0; k < cells; k++) {
        m.cp().post(eq(isEq(visit[k], i), isEq(xi, k)));
      }
    }

    out.put("x", x);
  }
}
