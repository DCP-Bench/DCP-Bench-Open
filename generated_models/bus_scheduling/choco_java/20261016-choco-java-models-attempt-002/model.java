import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Bus scheduling: a day is split into 6 successive 4-hour slots, repeating cyclically.
// Each bus runs 8 successive hours (two slots). Choose how many buses start in each slot
// so that every slot has enough buses on duty, using as few buses as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] demand = inst.getIntArray("demands");
    int k = demand.length;

    int total = 0;
    for (int d : demand) total += d;

    // x[i] is the number of buses that start at the beginning of slot i
    IntVar[] x = m.intVarArray("x", k, 0, total);

    // in each slot, the buses that started in this slot and the previous slot meet the demand.
    // The day repeats, so the previous slot of slot 0 is the last slot.
    for (int i = 0; i < k; i++) {
      int prev = (i + k - 1) % k;
      m.sum(new IntVar[]{x[i], x[prev]}, ">=", demand[i]).post();
    }

    // minimise the total number of buses
    IntVar buses = m.intVar("buses", 0, total * k, true);
    m.sum(x, "=", buses).post();
    m.setObjective(Model.MINIMIZE, buses);

    out.put("x", x);
  }
}
