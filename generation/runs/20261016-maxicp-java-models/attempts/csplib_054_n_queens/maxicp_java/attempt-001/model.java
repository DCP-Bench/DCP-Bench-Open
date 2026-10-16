import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Place n queens on an n x n chessboard so that no two queens attack each other.
// Row i holds the queen in column queens[i], columns numbered 1 to n.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // the position of the queen in each row is a column between 1 and n
    CPIntVar[] queens = m.intVarArray(n, 1, n);

    // no two queens in the same column
    m.cp().post(allDifferent(queens));

    // no two queens on the same diagonal, in either direction
    CPIntVar[] upDiagonal = new CPIntVar[n];
    CPIntVar[] downDiagonal = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      upDiagonal[i] = plus(queens[i], i);
      downDiagonal[i] = minus(queens[i], i);
    }
    m.cp().post(allDifferent(upDiagonal));
    m.cp().post(allDifferent(downDiagonal));

    out.put("queens", queens);
  }
}
