import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// All-interval series of size n: arrange the pitch classes 0 to n-1 in a series so that the
// intervals between neighbouring notes are exactly the values 1 to n-1, each occurring once.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // x[i]: the pitch class at position i of the series
    IntVar[] x = m.intVarArray("x", n, 0, n - 1);
    // diffs[i]: the interval between the notes at positions i and i+1
    IntVar[] diffs = m.intVarArray("diffs", n - 1, 1, n - 1);

    // each pitch class occurs exactly once
    m.allDifferent(x, "AC").post();

    // the signed step from one note to the next, and its absolute size as the interval
    for (int i = 0; i < n - 1; i++) {
      IntVar step = m.intVar("step" + i, -(n - 1), n - 1);
      m.arithm(step, "=", x[i + 1].sub(x[i]).intVar()).post();
      m.absolute(diffs[i], step).post();
    }

    // the intervals cover the full set 1 to n-1, each exactly once
    m.allDifferent(diffs, "AC").post();

    // search: dom/wdeg over the pitch classes and then the intervals, with Luby restarts.
    // The default search timed out for n = 20.
    IntVar[] all = new IntVar[n + n - 1];
    System.arraycopy(x, 0, all, 0, n);
    System.arraycopy(diffs, 0, all, n, n - 1);
    m.getSolver().setSearch(Search.domOverWDegSearch(all));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("x", x);
    out.put("diffs", diffs);
  }
}
