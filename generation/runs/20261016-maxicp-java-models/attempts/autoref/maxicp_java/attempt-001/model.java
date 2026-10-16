// Autoreferential series: find a non-empty series S = (s0, s1, ..., sn, sn+1) such that
// s_i is the number of occurrences of i in S for each i from 0 to n, and s_{n+1} = m.
import static org.maxicp.cp.CPFactory.*;

import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int mValue = inst.getInt("m");
    // the series has n + 2 terms, s0 .. sn+1; every term is a count, so it lies in 0 .. n+1
    int len = n + 2;
    CPIntVar[] s = new CPIntVar[len];
    for (int k = 0; k < len; k++) {
      s[k] = m.intVar(0, n + 1);
    }

    // the last term sn+1 equals m
    m.cp().post(eq(s[n + 1], mValue));

    // for each i from 0 to n, si is the number of occurrences of i in S
    for (int i = 0; i <= n; i++) {
      // hits[k] = 1 when the term at position k equals i
      CPBoolVar[] hits = new CPBoolVar[len];
      for (int k = 0; k < len; k++) {
        hits[k] = isEq(s[k], i);
      }
      // si is the number of occurrences of i: the sum of the hits equals si
      m.cp().post(sum(hits, s[i]));
    }

    out.put("s", s);
  }
}
