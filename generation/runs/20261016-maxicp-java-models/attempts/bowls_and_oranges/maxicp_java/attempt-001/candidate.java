// Bowls and oranges: n bowls in a line at 1 meter intervals; place m oranges, at
// most one per bowl, so that no three oranges A, B, C have the distance A-B equal
// to the distance B-C. Print the bowls holding oranges, in ascending order.
// Bowls are numbered from 1 (the first bowl in the line is bowl 1); the model
// searches with 0-based positions and reports positions plus one.

import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");   // number of bowls
    int k = inst.getInt("m");   // number of oranges

    // x[i] is the bowl holding the i-th orange, from 0 to n-1.
    CPIntVar[] x = m.intVarArray(k, 0, n - 1);

    // The oranges are in ascending order, and no bowl holds two oranges.
    for (int i = 0; i + 1 < k; i++) {
      m.cp().post(ge(x[i + 1], plus(x[i], 1)));
    }

    // occ[p] is 1 when bowl p holds an orange: some x[i] is p.
    CPBoolVar[] occ = m.boolVarArray(n);
    for (int p = 0; p < n; p++) {
      CPIntVar[] hits = new CPIntVar[k];
      for (int i = 0; i < k; i++) hits[i] = isEq(x[i], p);
      m.cp().post(eq(sum(hits), occ[p]));
    }

    // No three bowls A < B < C with B - A = C - B may all hold oranges:
    // for every bowl a and step d, one of the three bowls a, a+d, a+2d is empty.
    for (int a = 0; a < n; a++) {
      for (int d = 1; a + 2 * d < n; d++) {
        m.cp().post(or(new CPBoolVar[] {not(occ[a]), not(occ[a + d]), not(occ[a + 2 * d])}));
      }
    }

    // Report bowl numbers from 1: the view plus(x[i], 1) is the bowl number.
    CPIntVar[] bowls = new CPIntVar[k];
    for (int i = 0; i < k; i++) bowls[i] = plus(x[i], 1);
    out.put("x", bowls);
  }
}
