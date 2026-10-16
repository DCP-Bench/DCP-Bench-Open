import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.search.strategy.selectors.values.IntDomainMin;
import org.chocosolver.solver.search.strategy.selectors.variables.FirstFail;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Bin packing: assign each item to one of the bins so that the total weight in each bin
// does not exceed the bin capacity.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] weights = inst.getIntArray("weights");
    int capacity = inst.getInt("capacity");
    int numBins = inst.getInt("num_bins");
    int n = weights.length;

    int total = 0;
    for (int w : weights) total += w;

    // bins[i] is the bin (0-indexed) that item i is put in
    IntVar[] bins = m.intVarArray("bins", n, 0, numBins - 1);

    // the total weight of the items in each bin
    IntVar[] load = m.intVarArray("load", numBins, 0, capacity);

    // the total weight of the items in each bin does not exceed the capacity
    m.binPacking(bins, weights, load, 0).post();

    // implied: every item is in some bin, so the loads add up to the total weight
    m.sum(load, "=", total).post();

    // branch on the bins with the first-fail rule, smallest bin first
    m.getSolver().setSearch(Search.intVarSearch(
        new FirstFail(m), new IntDomainMin(), bins));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("bins", bins);
  }
}
