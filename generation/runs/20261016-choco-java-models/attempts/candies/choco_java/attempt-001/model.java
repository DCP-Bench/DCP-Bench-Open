import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Candies: give each child in a line at least one candy, so that a child with a higher
// rating than a neighbour gets more candies than that neighbour, and minimise the total.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] rating = inst.getIntArray("ratings");
    int n = rating.length;
    IntVar[] x = m.intVarArray("x", n, 1, n);  // candies of each child; no child needs more than n

    // a child with a higher rating than a neighbour gets more candies than that neighbour
    for (int i = 0; i + 1 < n; i++) {
      if (rating[i] > rating[i + 1]) m.arithm(x[i], ">", x[i + 1]).post();
      else if (rating[i] < rating[i + 1]) m.arithm(x[i], "<", x[i + 1]).post();
      // equal ratings: no constraint between the two neighbours
    }

    // minimise the total number of candies
    IntVar z = m.sum("z", x);
    m.setObjective(Model.MINIMIZE, z);

    out.put("x", x);
    out.put("z", z);
  }
}
