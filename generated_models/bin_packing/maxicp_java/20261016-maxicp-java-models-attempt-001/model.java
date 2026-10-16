import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Bin packing: assign each item to a bin so that the total weight of the items
// in each bin does not exceed the capacity. Bins are numbered from 0.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] weights = inst.getIntArray("weights");
    int capacity = inst.getInt("capacity");
    int numBins = inst.getInt("num_bins");
    int n = weights.length;

    // bins[i] is the bin item i is assigned to
    CPIntVar[] bins = m.intVarArray(n, 0, numBins - 1);

    // the total weight of the items in each bin does not exceed the capacity
    for (int b = 0; b < numBins; b++) {
      CPIntVar[] load = new CPIntVar[n];
      for (int i = 0; i < n; i++) {
        // the weight of item i counts for bin b when item i is assigned to bin b
        load[i] = mul(isEq(bins[i], b), weights[i]);
      }
      m.cp().post(le(sum(load), capacity));
    }

    out.put("bins", bins);
  }
}
