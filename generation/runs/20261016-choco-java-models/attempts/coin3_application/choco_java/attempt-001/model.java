import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Coin problem: choose how many coins of each denomination to hold so that every
// amount from 1 to max-1 can be paid exactly, minimising the total number of coins.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] d = inst.getIntArray("denominations");   // coin values
    int maxAmount = inst.getInt("max_amount_to_pay"); // amounts 1..maxAmount-1 must be payable
    int n = d.length;

    // x[i]: number of coins of denomination d[i]
    // no amount below maxAmount needs more than (maxAmount-1)/d[i] coins of one type
    IntVar[] x = new IntVar[n];
    for (int i = 0; i < n; i++) {
      x[i] = m.intVar("x" + i, 0, (maxAmount - 1) / d[i]);
    }

    // every amount a from 1 to maxAmount-1 can be paid exactly with the coins held
    for (int a = 1; a < maxAmount; a++) {
      // y[i]: number of coins of denomination d[i] used to pay the amount a
      IntVar[] y = new IntVar[n];
      for (int i = 0; i < n; i++) {
        y[i] = m.intVar("y" + a + "_" + i, 0, a / d[i]);
      }
      // the coins used add up to exactly a
      m.scalar(y, d, "=", a).post();
      // only coins that are held can be used
      for (int i = 0; i < n; i++) {
        m.arithm(y[i], "<=", x[i]).post();
      }
    }

    // minimise the total number of coins held
    IntVar total = m.sum("total", x);
    m.setObjective(Model.MINIMIZE, total);

    out.put("x", x);
  }
}
