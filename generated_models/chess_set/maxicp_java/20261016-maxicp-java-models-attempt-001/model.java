// Boxwood chess sets: decide how many small and large sets to make each week
// so as to maximize profit. Small set: 3 lathe-hours, 1 kg boxwood, profit $5.
// Large set: 2 lathe-hours, 3 kg boxwood, profit $20.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // number of small sets and large sets made each week
    CPIntVar small = m.intVar(0, 160);
    CPIntVar large = m.intVar(0, 160);

    // four lathes, each working a 40 hour week, give 160 lathe-hours per week
    // small set needs 3 hours, large set needs 2 hours
    m.cp().post(le(sum(mul(small, 3), mul(large, 2)), 160));

    // only 200 kg of boxwood can be obtained per week
    // small set needs 1 kg, large set needs 3 kg
    m.cp().post(le(sum(small, mul(large, 3)), 200));

    // profit: $5 per small set and $20 per large set
    CPIntVar profit = sum(mul(small, 5), mul(large, 20));

    // maximize the profit
    m.maximize(profit);

    out.put("small_set", small);
    out.put("large_set", large);
    out.put("max_profit", profit);
  }
}
