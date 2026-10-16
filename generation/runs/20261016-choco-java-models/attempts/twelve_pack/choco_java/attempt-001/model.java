import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Twelve-pack problem: choose how many packs of each size to buy so that the number of
// items meets or exceeds the target, and the total number of items is as small as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] packs = inst.getIntArray("packs");
    int target = inst.getInt("target");
    int k = packs.length;

    // counts[i] = number of packs of size packs[i] bought; buying more than
    // ceil(target / size) packs of one size never helps
    IntVar[] counts = new IntVar[k];
    for (int i = 0; i < k; i++) {
      counts[i] = m.intVar("counts_" + i, 0, target / packs[i] + 1);
    }

    // total number of items bought
    int maxTotal = 0;
    for (int i = 0; i < k; i++) maxTotal = Math.max(maxTotal, packs[i]);
    IntVar total = m.intVar("total", target, (target + maxTotal) * 2, true);

    // the items in all packs add up to the total
    m.scalar(counts, packs, "=", total).post();

    // the total meets or exceeds the target
    m.arithm(total, ">=", target).post();

    // minimise the excess over the target: the closest combination that reaches it
    m.setObjective(Model.MINIMIZE, total);

    out.put("counts", counts);
  }
}
