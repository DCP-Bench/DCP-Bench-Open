import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Magic sequence: find a sequence x_0..x_{n-1} of integers between 0 and n-1 such that
// for every i, the number i occurs exactly x_i times in the sequence.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    IntVar[] x = m.intVarArray("x", n, 0, n - 1);

    // every entry of the sequence is a value between 0 and n-1 (given by the domains above)

    // the sequence has n entries, so the occurrences of all values add up to n
    m.sum(x, "=", n).post();

    // for each i, the number i occurs exactly x_i times in the sequence
    for (int i = 0; i < n; i++) {
      m.count(i, x, x[i]).post();
    }

    out.put("x", x);
  }
}
