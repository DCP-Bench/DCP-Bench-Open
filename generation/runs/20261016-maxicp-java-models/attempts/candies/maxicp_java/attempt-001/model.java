import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Candies: Alice gives candies to children sitting in a line, each with a rating.
// Every child gets at least 1 candy. Of two neighbours, the one with the higher rating
// gets more candies. Minimise the total number of candies.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] ratings = inst.getIntArray("ratings");
    int n = ratings.length;

    // the number of candies for each child; a child never needs more than n candies
    // (one more than the chain of strictly lower ratings to the left)
    CPIntVar[] x = m.intVarArray(n, 1, n);

    // if two children sit next to each other, the one with the higher rating gets more candies
    for (int i = 0; i + 1 < n; i++) {
      if (ratings[i] > ratings[i + 1]) {
        m.cp().post(ge(x[i], plus(x[i + 1], 1)));
      } else if (ratings[i] < ratings[i + 1]) {
        m.cp().post(ge(x[i + 1], plus(x[i], 1)));
      }
    }

    // the total number of candies
    CPIntVar z = sum(x);

    // minimise the total number of candies
    m.minimize(z);

    out.put("z", z);
    out.put("x", x);
  }
}
