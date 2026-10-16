import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Heterosquare of order n: an n x n square of distinct integers 1..n^2 whose row,
// column and diagonal sums are all different from each other.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int nn = n * n;

    // the square: x[i][j] is the element in row i, column j
    IntVar[][] x = m.intVarMatrix("x", n, n, 1, nn);

    // elements are distinct integers from 1 to n^2
    IntVar[] cells = new IntVar[nn];
    for (int i = 0; i < n; i++)
      for (int j = 0; j < n; j++) cells[i * n + j] = x[i][j];
    m.allDifferent(cells, "AC").post();

    // sums of the rows, columns and the two diagonals
    IntVar[] sums = new IntVar[2 * n + 2];
    int k = 0;

    // the sum of each row
    for (int i = 0; i < n; i++) sums[k++] = m.sum("row" + i, x[i]);

    // the sum of each column
    for (int j = 0; j < n; j++) {
      IntVar[] col = new IntVar[n];
      for (int i = 0; i < n; i++) col[i] = x[i][j];
      sums[k++] = m.sum("col" + j, col);
    }

    // the sum of the main diagonal and of the anti-diagonal
    IntVar[] diag = new IntVar[n];
    IntVar[] anti = new IntVar[n];
    for (int i = 0; i < n; i++) {
      diag[i] = x[i][i];
      anti[i] = x[i][n - 1 - i];
    }
    sums[k++] = m.sum("diag", diag);
    sums[k++] = m.sum("anti", anti);

    // the sums of rows, columns and diagonals are all different
    m.allDifferent(sums, "AC").post();

    out.put("x", x);
  }
}
