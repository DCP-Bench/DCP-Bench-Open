// Costas array of order n: n marks on an n x n grid, one per row and one per column,
// in which the n(n-1)/2 vectors between the marks are all different.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // the marks X_1..X_n form a permutation of 1..n (one mark per row and column)
    CPIntVar[] x = m.intVarArray(n, 1, n);
    m.cp().post(allDifferent(x));

    // difference triangle: for each length l, the differences X_i - X_{i+l} are all different
    for (int l = 1; l <= n - 1; l++) {
      // the n-l differences of line l
      CPIntVar[] d = m.intVarArray(n - l, -(n - 1), n - 1);
      for (int i = 0; i < n - l; i++) {
        // X_i - X_{i+l} is the difference d_i, so X_{i+l} + d_i = X_i
        m.cp().post(sum(new CPIntVar[] { x[i + l], d[i] }, x[i]));
      }
      // every line of the difference triangle holds no value twice
      m.cp().post(allDifferent(d));
    }

    out.put("costas", x);
  }
}
