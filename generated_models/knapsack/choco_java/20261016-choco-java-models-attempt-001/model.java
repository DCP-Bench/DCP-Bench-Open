import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// 0-1 knapsack: choose which items to put in the backpack so that the total weight
// stays within the capacity and the total value is as large as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] values = inst.getIntArray("values");
    int[] weights = inst.getIntArray("weights");
    int capacity = inst.getInt("capacity");
    int n = values.length;

    // x[i] = true if item i is taken
    BoolVar[] x = m.boolVarArray("x", n);

    // total weight of the items taken, at most the capacity of the backpack
    int sumWeights = 0, sumValues = 0;
    for (int i = 0; i < n; i++) { sumWeights += weights[i]; sumValues += values[i]; }
    IntVar totalWeight = m.intVar("total weight", 0, Math.min(capacity, sumWeights), true);
    IntVar totalValue = m.intVar("total value", 0, sumValues, true);

    // the items taken weigh at most the capacity, and their values add up to the total value
    m.knapsack(x, totalWeight, totalValue, weights, values).post();
    totalWeight.le(capacity).post();

    // maximise the total value of the items in the backpack
    m.setObjective(Model.MAXIMIZE, totalValue);

    out.put("x", x);
  }
}
