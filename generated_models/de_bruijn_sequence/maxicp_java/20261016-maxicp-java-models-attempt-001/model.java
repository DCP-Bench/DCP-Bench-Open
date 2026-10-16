// de Bruijn sequence of order n on an alphabet of size base:
// a cyclic sequence of base^n symbols in which every length-n string
// over the alphabet occurs exactly once as a substring.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int base = inst.getInt("base");
    int n = inst.getInt("n");
    int len = 1;
    for (int i = 0; i < n; i++) len *= base;

    // the sequence: len symbols, each one from the alphabet 0..base-1
    CPIntVar[] x = m.intVarArray(len, 0, base - 1);

    // each length-n window of the cyclic sequence, read as a base-`base`
    // number, is a value in 0..len-1
    CPIntVar[] w = m.intVarArray(len, 0, len - 1);
    for (int i = 0; i < len; i++) {
      // the window starting at position i, wrapping around the end, spells the number w[i]
      CPIntVar[] digits = new CPIntVar[n];
      int weight = 1;
      for (int j = n - 1; j >= 0; j--) {
        digits[j] = mul(x[(i + j) % len], weight);
        weight *= base;
      }
      m.cp().post(eq(w[i], sum(digits)));
    }

    // every length-n string occurs exactly once: all windows are different
    m.cp().post(allDifferent(w));

    out.put("de_bruijn", x);
  }
}
