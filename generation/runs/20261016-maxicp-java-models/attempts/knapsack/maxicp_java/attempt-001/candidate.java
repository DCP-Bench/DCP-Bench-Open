import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// 0-1 knapsack: a hiker picks items to put in a backpack.
// Each item has a value and a weight. The hiker maximizes the total value
// of the items taken without exceeding the weight capacity of the backpack.
// x[i] is true when item i is taken.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] values = inst.getIntArray("values");
    int[] weights = inst.getIntArray("weights");
    int capacity = inst.getInt("capacity");
    int n = values.length;

    // which items to take
    CPBoolVar[] x = m.boolVarArray(n);

    // the total weight of the items taken does not exceed the weight capacity
    CPIntVar[] takenWeights = new CPIntVar[n];
    CPIntVar[] takenValues = new CPIntVar[n];
    int totalValue = 0;
    for (int i = 0; i < n; i++) {
      takenWeights[i] = mul(x[i], weights[i]);
      takenValues[i] = mul(x[i], values[i]);
      totalValue += values[i];
    }
    m.cp().post(le(sum(takenWeights), capacity));

    // maximize the total value of the items taken
    CPIntVar obj = m.intVar(0, totalValue);
    m.cp().post(eq(obj, sum(takenValues)));
    m.maximize(obj);

    out.put("x", x);
  }
}
