import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Bus scheduling: buses run 8 hours, which is two successive 4-hour slots, and the day
// has six 4-hour slots that wrap around. Find the minimum number of buses, and how many
// start in each slot, so that the buses available in each slot meet that slot's demand.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] demands = inst.getIntArray("demands");
    int n = demands.length;

    int maxDemand = 0;
    for (int d : demands) maxDemand = Math.max(maxDemand, d);

    // the number of buses starting in each time slot; a bus starting in slot i covers slot i and slot i+1
    // more buses starting in one slot than the largest demand are never needed
    CPIntVar[] x = m.intVarArray(n, 0, maxDemand);

    // each slot's demand is met by the buses that start in that slot and the buses that
    // started in the previous slot, which are still driving (the day wraps around)
    for (int j = 0; j < n; j++) {
      int prev = (j + n - 1) % n;
      m.cp().post(ge(sum(new CPIntVar[] {x[j], x[prev]}), demands[j]));
    }

    // minimise the total number of buses
    m.minimize(sum(x));

    out.put("x", x);
  }
}
