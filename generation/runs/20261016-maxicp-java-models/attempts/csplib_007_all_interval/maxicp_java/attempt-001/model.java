// All-interval series of size n: a permutation x of 0..n-1 whose
// neighbouring absolute differences form a permutation of 1..n-1.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // the series s = (s_1, ..., s_n) is a permutation of 0..n-1
    CPIntVar[] x = m.intVarArray(n, 0, n - 1);
    m.cp().post(allDifferent(x));

    // the interval vector v holds the values 1..n-1
    CPIntVar[] diffs = m.intVarArray(n - 1, 1, n - 1);

    // v is a permutation of 1..n-1: every interval occurs exactly once
    m.cp().post(allDifferent(diffs));

    // each interval is the absolute difference between neighbouring notes
    for (int i = 0; i < n - 1; i++) {
      CPIntVar signed = sum(new CPIntVar[] { x[i + 1], minus(x[i]) });
      CPIntVar absolute = max(new CPIntVar[] { signed, minus(signed) });
      m.cp().post(eq(diffs[i], absolute));
    }

    out.put("diffs", diffs);
    out.put("x", x);
  }
}
