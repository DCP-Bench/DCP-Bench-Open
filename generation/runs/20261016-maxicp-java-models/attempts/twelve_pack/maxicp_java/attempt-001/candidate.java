// Twelve-pack problem: given a target number of items and a set of pack sizes,
// find the closest combination of packs that meets or exceeds the target.
// Report the number of packs of each size used.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the pack sizes and the target number of items
    int[] packs = inst.getIntArray("packs");
    int target = inst.getInt("target");
    int n = packs.length;

    // the number of packs of each size used
    CPIntVar[] counts = m.intVarArray(n, 0, target);

    // the items in the packs used: each size times its number of packs
    CPIntVar[] items = new CPIntVar[n];
    int maxItems = 0;
    for (int i = 0; i < n; i++) {
      items[i] = mul(counts[i], packs[i]);
      maxItems += target * packs[i];
    }
    CPIntVar total = m.intVar(0, maxItems);
    m.cp().post(eq(total, sum(items)));

    // the combination meets or exceeds the target
    m.cp().post(ge(total, target));

    // the closest combination: the total is as small as possible
    m.minimize(total);

    out.put("counts", counts);
  }
}
