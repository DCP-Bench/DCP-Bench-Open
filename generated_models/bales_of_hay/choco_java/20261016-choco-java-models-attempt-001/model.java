// Bales of hay: n bales were weighed in all pairs, and the pair weights were written down
// in numerical order without matching them to pairs. Find the weight of each bale, sorted
// nondecreasing, so that the sorted pair sums are exactly the given weights.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");                  // number of bales
    int[] weights = inst.getIntArray("weights"); // the pair weights, in numerical order
    int pairs = weights.length;                // n * (n - 1) / 2 combinations of two

    int lo = weights[0];
    int hi = weights[pairs - 1];

    // the weight of each bale; a bale never weighs more than the heaviest pair
    IntVar[] bales = m.intVarArray("bale", n, 0, hi, true);

    // the bales are listed in nondecreasing weight
    for (int i = 0; i + 1 < n; i++) {
      m.arithm(bales[i], "<=", bales[i + 1]).post();
    }

    // one sum per combination of two bales
    IntVar[] pairSums = new IntVar[pairs];
    int k = 0;
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        pairSums[k] = m.intVar("pair" + k, 0, 2 * hi, true);
        m.sum(new IntVar[]{bales[i], bales[j]}, "=", pairSums[k]).post();
        k++;
      }
    }

    // the combination weights, in numerical order, are the given weights
    IntVar[] sorted = m.intVarArray("sorted", pairs, lo, hi, true);
    m.sort(pairSums, sorted).post();
    for (int p = 0; p < pairs; p++) {
      m.arithm(sorted[p], "=", weights[p]).post();
    }

    out.put("bales", bales);
  }
}
