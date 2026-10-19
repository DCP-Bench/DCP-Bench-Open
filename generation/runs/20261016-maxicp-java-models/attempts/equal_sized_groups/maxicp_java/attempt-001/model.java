import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Divide a sorted list of N elements into K consecutive groups by K-1 break points, so that
// the total deviation of each group's size from round(N/K) is minimised. Equal values must stay in one group.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] a = inst.getIntArray("a");
    int k = inst.getInt("k");
    int n = a.length;
    // round(N/K), halves rounded up
    int target = (2 * n + k) / (2 * k);

    // X[i] is the 1-based position of the last element of group i; X[0] = 0 and X[k] = N are the ends
    CPIntVar[] X = new CPIntVar[k + 1];
    X[0] = m.intVar(0, 0);
    X[k] = m.intVar(n, n);
    for (int i = 1; i < k; i++) {
      X[i] = m.intVar(1, n - 1);
    }

    // the elements of group i are the ones between the two break points, so its size is X[i] - X[i-1]
    CPIntVar[] err = new CPIntVar[k];
    for (int i = 1; i <= k; i++) {
      // every group holds at least one element
      CPIntVar size = m.intVar(1, n);
      m.cp().post(sum(new CPIntVar[]{X[i - 1], size}, X[i]));
      // the deviation of the group size from round(N/K) is |target - size|
      CPIntVar dev = m.intVar(-n, n);
      m.cp().post(sum(new CPIntVar[]{size, dev}, target));
      err[i - 1] = m.intVar(0, n);
      m.cp().post(ge(err[i - 1], dev));
      m.cp().post(ge(err[i - 1], minus(dev)));
    }

    // a break may not split a run of equal values: the element before and the element after it differ
    for (int i = 1; i < k; i++) {
      for (int p = 1; p < n; p++) {
        if (a[p - 1] == a[p]) {
          m.cp().post(neq(X[i], p));
        }
      }
    }

    // minimise the total deviation over all groups
    CPIntVar total = m.intVar(0, n * k);
    m.cp().post(eq(total, sum(err)));
    m.minimize(total);

    // the declared output: the K-1 break points, 1-based
    CPIntVar[] breaks = new CPIntVar[k - 1];
    for (int i = 1; i < k; i++) {
      breaks[i - 1] = X[i];
    }
    out.put("x", breaks);
  }
}
