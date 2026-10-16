import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Set card game: find three distinct cards (0-based indices) that form a set,
// where each of the four features is either all the same or all different.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] cards = inst.getIntMatrix("cards_data");   // cards[c] = {number, fill, color, shape}
    int n = cards.length;

    // winning_cards[k]: 0-based index of the k-th card of the set.
    // Strictly increasing, so the three distinct cards come in one fixed order.
    IntVar[] w = m.intVarArray("card", 3, 0, n - 1);
    m.increasing(w, 1).post();

    String[] features = {"number", "fill", "color", "shape"};
    for (int f = 0; f < features.length; f++) {
      // the feature value of each of the three cards, read from the card data
      int[] column = new int[n];
      for (int c = 0; c < n; c++) column[c] = cards[c][f];
      IntVar[] vals = new IntVar[3];
      for (int k = 0; k < 3; k++) {
        vals[k] = m.intVar(features[f] + "_" + k, 1, 3);
        m.element(vals[k], column, w[k]).post();
      }

      // for this feature the three cards are all the same or all different:
      // the number of distinct values among the three cards is 1 or 3
      IntVar distinct = m.intVar("distinct_" + features[f], new int[]{1, 3});
      m.nValues(vals, distinct).post();
    }

    out.put("winning_cards", w);
  }
}
