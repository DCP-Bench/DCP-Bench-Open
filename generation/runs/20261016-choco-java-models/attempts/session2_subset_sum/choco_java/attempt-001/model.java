import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Bank van coin bags: find how many bags of each type were stolen so that
// the stolen bags hold exactly the total number of lost coins.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int total = inst.getInt("total_coins_lost");
    int[] coinNumbers = inst.getIntArray("coin_numbers");
    int n = coinNumbers.length;

    // bags[i]: number of bags of type i stolen. A bag of type i holds
    // coinNumbers[i] coins, so at most total / coinNumbers[i] bags of that type fit.
    IntVar[] bags = new IntVar[n];
    for (int i = 0; i < n; i++) {
      bags[i] = m.intVar("bags_" + coinNumbers[i], 0, total / coinNumbers[i]);
    }

    // the stolen bags hold the total number of lost coins
    m.scalar(bags, coinNumbers, "=", total).post();

    out.put("bags", bags);
  }
}
