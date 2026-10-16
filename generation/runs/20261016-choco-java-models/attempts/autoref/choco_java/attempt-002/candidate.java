import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Autoreferential series: find a series S = (s0, s1, ..., sn, sn+1) such that s_i is the
// number of occurrences of i in S for each i from 0 to n, and the last term s_{n+1} = m.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int mv = inst.getInt("m");
    int len = n + 2;

    // the series has n+2 terms (s0 .. sn+1). Every term is a count of some value i in 0..n,
    // and every value in S must itself be counted, so each term lies between 0 and n
    IntVar[] s = m.intVarArray("s", len, 0, n);

    // s_i is the number of occurrences of i in S, for each i from 0 to n
    for (int i = 0; i <= n; i++) {
      m.count(i, s, s[i]).post();
    }

    // the last term is m
    m.arithm(s[n + 1], "=", mv).post();

    out.put("s", s);
  }
}
