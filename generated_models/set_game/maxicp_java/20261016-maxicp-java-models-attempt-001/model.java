// Set card game: pick three cards out of the dealt cards that form a set.
// Each card has four features (number, shading, colour, shape); each feature
// must be the same on all three cards or different on all three cards.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] cards = inst.getIntMatrix("cards_data");
    int n = cards.length;

    // the winning set is three different cards
    CPIntVar[] w = m.intVarArray(3, 0, n - 1);
    m.cp().post(allDifferent(w));

    // for every feature: the three cards all show the same version, or all different versions
    for (int f = 0; f < 4; f++) {
      int[] column = new int[n];
      for (int j = 0; j < n; j++) column[j] = cards[j][f];
      CPIntVar[] v = new CPIntVar[3];
      for (int i = 0; i < 3; i++) v[i] = element(column, w[i]);
      // exactly two equal is not allowed: the three equality tests must agree
      CPBoolVar e01 = isEq(v[0], v[1]);
      CPBoolVar e12 = isEq(v[1], v[2]);
      CPBoolVar e02 = isEq(v[0], v[2]);
      m.cp().post(eq(e01, e12));
      m.cp().post(eq(e12, e02));
    }

    out.put("winning_cards", w);
  }
}
