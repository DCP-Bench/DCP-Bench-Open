import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Joe's account number x is a list of n integers, with the digits 0 to n-1 in some order.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] sets = inst.getIntMatrix("sets");
    int k = inst.getInt("num_correct_digits");
    int n = sets[0].length;

    // the account number has all digits from 0 to n-1 in some order
    CPIntVar[] x = m.intVarArray(n, 0, n - 1);
    m.cp().post(allDifferent(x));

    // in each set just a specific number of the digits are in their correct position
    for (int s = 0; s < sets.length; s++) {
      CPBoolVar[] correct = new CPBoolVar[n];
      for (int i = 0; i < n; i++) {
        correct[i] = isEq(x[i], sets[s][i]);
      }
      m.cp().post(eq(sum(correct), k));
    }

    // print Joe's account number
    out.put("x", x);
  }
}
