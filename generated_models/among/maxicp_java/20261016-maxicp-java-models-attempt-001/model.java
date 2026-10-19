// Among: x is an array of n entries, each in 0..7.
// Requires exactly m values in x to take one of the values in v.

import java.util.Set;
import java.util.TreeSet;

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int cnt = inst.getInt("m");
    int[] v = inst.getIntArray("v");

    // All other values may be anything from 0 to 7.
    CPIntVar[] x = m.intVarArray(n, 0, 7);

    // Only the distinct values of v count, so each entry of x matches v at most once.
    Set<Integer> distinct = new TreeSet<>();
    for (int value : v) distinct.add(value);

    // Each entry of x takes one of the values in v: it counts as 1 when it equals one of them.
    CPIntVar[] inV = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      CPIntVar[] matches = new CPIntVar[distinct.size()];
      int j = 0;
      for (int value : distinct) {
        matches[j++] = isEq(x[i], value);
      }
      inV[i] = sum(matches);
    }

    // Requires exactly m values in x to take one of the values in v.
    m.cp().post(eq(sum(inV), cnt));

    out.put("x", x);
  }
}
