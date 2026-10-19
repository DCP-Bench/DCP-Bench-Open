import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Find a fifth number d >= 0 such that adding d to the set {1, 3, 8, 120}
// keeps the property: the product of any two integers of the set is one less
// than a perfect square.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int maxVal = inst.getInt("max_val");

    // the fifth number is at least 0 and at most the instance bound
    CPIntVar d = m.intVar(0, maxVal);

    // the four given integers
    int[] set = {1, 3, 8, 120};

    // the largest product that can occur is 120 * max_val + 1
    long maxProduct = 120L * maxVal + 1;
    int maxRoot = 0;
    while ((long) (maxRoot + 1) * (maxRoot + 1) <= maxProduct) {
      maxRoot++;
    }

    // table of squares 0, 1, 4, ..., maxRoot^2
    int[] squares = new int[maxRoot + 1];
    for (int i = 0; i <= maxRoot; i++) {
      squares[i] = i * i;
    }

    for (int k : set) {
      // the product of any two integers is one less than a perfect square:
      // the product of k and the fifth number, plus one, is a square
      CPIntVar root = m.intVar(0, maxRoot);
      CPIntVar sq = m.intVar(0, (int) maxProduct);
      m.cp().post(eq(sq, element(squares, root)));
      m.cp().post(eq(sq, plus(mul(d, k), 1)));
    }

    out.put("number", d);
  }
}
