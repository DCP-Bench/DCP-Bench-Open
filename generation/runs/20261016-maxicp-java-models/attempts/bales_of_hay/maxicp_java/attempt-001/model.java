// Bales of hay: the bales were weighed in all pairs, and the pair weights were
// written down in numerical order without saying which pair gave which weight.
// Find the weight of each bale from the list of pair weights.

import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int[] weights = inst.getIntArray("weights");
    int numPairs = weights.length;

    // The weight of each bale is between 0 and the heaviest pair weight.
    int maxWeight = 0;
    for (int w : weights) maxWeight = Math.max(maxWeight, w);

    // The weight of each bale.
    CPIntVar[] bales = m.intVarArray(n, 0, maxWeight);

    // Each pair of bales (i, j) with i < j gives one weight in the list.
    // Pair k has the sum bales[i] + bales[j]; the list position of that
    // weight is pos[k], and it is a bijection onto the list.
    CPIntVar[] pos = m.intVarArray(numPairs, 0, numPairs - 1);
    int k = 0;
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        // the weight of the two bales together is one of the weights in the list
        m.cp().post(eq(sum(new CPIntVar[] {bales[i], bales[j]}), element(weights, pos[k])));
        k++;
      }
    }

    // Every weight in the list is used by exactly one pair of bales.
    m.cp().post(allDifferent(pos));

    out.put("bales", bales);
  }
}
