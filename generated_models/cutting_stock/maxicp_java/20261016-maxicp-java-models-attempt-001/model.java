// Cutting stock: raw rolls of one width are cut into pieces of several widths.
// Each cutting pattern gives a number of pieces of each width. Choose how many
// rolls to cut with each pattern so that every width meets its order and the
// total number of raw rolls cut is minimal.

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int numPatterns = inst.getInt("num_patterns");
    int[] orders = inst.getIntArray("orders");          // demand per width
    int[][] rollsPerWidth = inst.getIntMatrix("num_rolls_width");  // [pattern][width]
    int numWidths = orders.length;

    // Upper bound on the number of times one pattern is cut: the total demand.
    int totalDemand = 0;
    for (int o : orders) totalDemand += o;

    // patterns_used[p] = number of raw rolls cut with pattern p
    CPIntVar[] used = m.intVarArray(numPatterns, 0, totalDemand);

    // every width meets its order: the pieces of that width cut from all rolls
    // add up to at least the number ordered
    for (int w = 0; w < numWidths; w++) {
      CPIntVar[] piecesOfWidth = new CPIntVar[numPatterns];
      for (int p = 0; p < numPatterns; p++) {
        piecesOfWidth[p] = mul(used[p], rollsPerWidth[p][w]);
      }
      m.cp().post(ge(sum(piecesOfWidth), orders[w]));
    }

    // total number of raw rolls cut, to be minimised
    CPIntVar totalRolls = m.intVar(0, numPatterns * totalDemand);
    m.cp().post(eq(totalRolls, sum(used)));
    m.minimize(totalRolls);

    out.put("min_rolls_cut", totalRolls);
    out.put("patterns_used", used);
  }
}
