import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// De Bruijn sequence B(base, n): a cyclic sequence over an alphabet of size base in which
// every string of length n occurs exactly once as a (cyclic) substring.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int base = inst.getInt("base");
    int n = inst.getInt("n");
    int len = 1;
    for (int t = 0; t < n; t++) len *= base;  // the sequence has base^n symbols

    // x[i]: the i-th symbol of the cyclic sequence
    IntVar[] x = m.intVarArray("x", len, 0, base - 1);

    // each length-n window, read cyclically from position i, is coded as a number in 0..len-1
    IntVar[] window = new IntVar[len];
    int[] weight = new int[n];
    int w = 1;
    for (int t = 0; t < n; t++) { weight[t] = w; w *= base; }
    for (int i = 0; i < len; i++) {
      IntVar[] digits = new IntVar[n];
      for (int t = 0; t < n; t++) digits[t] = x[(i + t) % len];
      window[i] = m.intVar("window" + i, 0, len - 1);
      m.scalar(digits, weight, "=", window[i]).post();
    }

    // there are base^n windows and base^n possible strings, so every string appears exactly once
    m.allDifferent(window, "AC").post();

    out.put("de_bruijn", x);
  }
}
