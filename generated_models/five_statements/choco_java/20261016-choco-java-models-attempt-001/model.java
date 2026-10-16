import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Five statements: each says "exactly k of these statements are false" for k = 1..5.
// Decide which statements are true.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = 5;
    // s[i]: statement i+1 is true
    BoolVar[] s = m.boolVarArray("statements", n);

    // the number of true statements
    IntVar trueCount = m.intVar("trueCount", 0, n);
    m.sum(s, "=", trueCount).post();

    // statement k (k = 1..5) is true exactly when exactly k statements are false,
    // that is exactly n - k statements are true
    for (int k = 1; k <= n; k++) {
      BoolVar holds = trueCount.eq(n - k).boolVar();
      m.arithm(s[k - 1], "=", holds).post();
    }

    out.put("statements", s);
  }
}
