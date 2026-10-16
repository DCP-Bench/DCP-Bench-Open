// Costas array: a permutation X of 1..n such that, for every length l, the differences
// X_i - X_{i+l} of the difference triangle are all different (no value repeated in a line).
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // X[i] = the row (1-based) of the mark in column i+1; one mark per row and column
    IntVar[] X = m.intVarArray("X", n, 1, n);
    m.allDifferent(X, "AC").post();

    // each line of the difference triangle: for length l, the differences
    // X_i - X_{i+l} must not contain any value twice
    for (int l = 1; l <= n - 1; l++) {
      IntVar[] line = m.intVarArray("d" + l, n - l, -(n - 1), n - 1);
      for (int i = 0; i < n - l; i++) {
        // line[i] = X_i - X_{i+l}
        m.arithm(line[i], "=", X[i], "-", X[i + l]).post();
      }
      m.allDifferent(line, "AC").post();
    }

    out.put("costas", X);
  }
}
