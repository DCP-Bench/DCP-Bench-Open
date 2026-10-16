// Heterosquare of order n: an n x n square of distinct integers from 1 to n^2
// such that the sums of the rows, the columns and the two diagonals are all different.
// Output x is the square, as a list of rows.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int cells = n * n;

    // the square: x[i][j] is the element in row i, column j (0-based)
    CPIntVar[][] x = new CPIntVar[n][];
    for (int i = 0; i < n; i++) {
      x[i] = m.intVarArray(n, 1, cells);
    }

    // the elements of the square are distinct integers from 1 to n^2
    CPIntVar[] elements = new CPIntVar[cells];
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        elements[i * n + j] = x[i][j];
      }
    }
    m.cp().post(allDifferent(elements));

    // each line sum is at most n values of at most n^2 each
    int sumMax = n * cells;

    // the sums of the rows, the columns and the two diagonals, in that order
    int lines = 2 * n + 2;
    CPIntVar[] lineSums = new CPIntVar[lines];
    for (int k = 0; k < lines; k++) {
      lineSums[k] = m.intVar(1, sumMax);
    }

    // the sum of row i is lineSums[i]
    for (int i = 0; i < n; i++) {
      m.cp().post(sum(x[i], lineSums[i]));
    }

    // the sum of column j is lineSums[n + j]
    for (int j = 0; j < n; j++) {
      CPIntVar[] column = new CPIntVar[n];
      for (int i = 0; i < n; i++) {
        column[i] = x[i][j];
      }
      m.cp().post(sum(column, lineSums[n + j]));
    }

    // the sum of the main diagonal is lineSums[2n], the sum of the anti-diagonal is lineSums[2n + 1]
    CPIntVar[] mainDiagonal = new CPIntVar[n];
    CPIntVar[] antiDiagonal = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      mainDiagonal[i] = x[i][i];
      antiDiagonal[i] = x[i][n - 1 - i];
    }
    m.cp().post(sum(mainDiagonal, lineSums[2 * n]));
    m.cp().post(sum(antiDiagonal, lineSums[2 * n + 1]));

    // the sums of the rows, the columns and the diagonals are all different
    m.cp().post(allDifferent(lineSums));

    out.put("x", x);
  }
}
