import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Cutting stock: cut as few raw rolls as possible so that every width gets at least its
// ordered number of pieces, each roll being cut by one of the given cutting patterns.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int numPatterns = inst.getInt("num_patterns");
    int[] orders = inst.getIntArray("orders");           // ordered pieces per width
    int[][] patternRows = inst.getIntMatrix("num_rolls_width");  // patternRows[p][w]: pieces of width w in pattern p
    int widths = orders.length;

    // patterns_used[p]: how many rolls are cut with pattern p; no pattern can be used more than the largest order
    int maxOrder = 0;
    for (int o : orders) maxOrder = Math.max(maxOrder, o);
    IntVar[] used = m.intVarArray("patterns_used", numPatterns, 0, maxOrder);

    // every width gets at least its ordered number of pieces
    for (int w = 0; w < widths; w++) {
      int[] piecesOfWidth = new int[numPatterns];
      for (int p = 0; p < numPatterns; p++) piecesOfWidth[p] = patternRows[p][w];
      m.scalar(used, piecesOfWidth, ">=", orders[w]).post();
    }

    // minimise the total number of raw rolls cut
    IntVar total = m.sum("min_rolls_cut", used);
    m.setObjective(Model.MINIMIZE, total);

    out.put("min_rolls_cut", total);
    out.put("patterns_used", used);
  }
}
