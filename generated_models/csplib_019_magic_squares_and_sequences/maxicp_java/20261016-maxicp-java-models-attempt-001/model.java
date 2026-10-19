// Magic sequence of length n: integers x_0, ..., x_{n-1} between 0 and n-1
// such that for all i in 0 to n-1, the number i occurs exactly x_i times in the sequence.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // the sequence x_0, ..., x_{n-1}, each value between 0 and n-1
    CPIntVar[] x = m.intVarArray(n, 0, n - 1);

    // for all i, the number i occurs exactly x_i times in the sequence
    for (int i = 0; i < n; i++) {
      CPBoolVar[] isI = new CPBoolVar[n];
      for (int j = 0; j < n; j++) {
        isI[j] = isEq(x[j], i);
      }
      m.cp().post(sum(isI, x[i]));
    }

    out.put("x", x);
  }
}
