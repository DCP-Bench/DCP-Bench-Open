import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Chess sets: decide how many small and large boxwood chess sets to make each week so as
// to maximise profit, subject to lathe hours and boxwood supply.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // number of small sets and large sets per week
    IntVar small = m.intVar("small_set", 0, 160);
    IntVar large = m.intVar("large_set", 0, 160);
    IntVar[] sets = {small, large};

    // lathe hours: four lathes, each working 40 hours a week, so 160 lathe-hours in total.
    // The small set takes 3 hours, the large set 2 hours.
    m.scalar(sets, new int[]{3, 2}, "<=", 160).post();

    // boxwood: only 200 kg per week can be obtained. The small set needs 1 kg, the large set 3 kg.
    m.scalar(sets, new int[]{1, 3}, "<=", 200).post();

    // profit: a small set sells for $5 and a large set for $20
    IntVar profit = m.intVar("max_profit", 0, 5 * 160 + 20 * 160, true);
    m.scalar(sets, new int[]{5, 20}, "=", profit).post();

    // maximise the weekly profit
    m.setObjective(Model.MAXIMIZE, profit);

    out.put("small_set", small);
    out.put("large_set", large);
    out.put("max_profit", profit);
  }
}
