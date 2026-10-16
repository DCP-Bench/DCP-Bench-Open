import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Product mix: choose how much of each product j to make, X[j] between 0 and u[j], so
// that the time needed, the sum of X[j] / a[j], stays within the available time b, and
// the total profit, the sum of c[j] * X[j], is as large as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] a = inst.getIntArray("a");     // units of product j made per unit of time
    int[] c = inst.getIntArray("c");     // profit per unit of product j
    int[] u = inst.getIntArray("u");     // upper bound on the production of product j
    int b = inst.getInt("b");            // available time
    int n = a.length;

    // X[j]: production quantity of product j
    IntVar[] X = new IntVar[n];
    for (int j = 0; j < n; j++) X[j] = m.intVar("X" + j, 0, u[j]);

    // time constraint: sum of X[j] / a[j] <= b. Multiply by L, the lcm of the a[j], to
    // keep the coefficients integral: sum of (L / a[j]) * X[j] <= b * L
    long L = 1;
    for (int j = 0; j < n; j++) L = lcm(L, a[j]);
    int[] timeWeight = new int[n];
    for (int j = 0; j < n; j++) timeWeight[j] = (int) (L / a[j]);
    m.scalar(X, timeWeight, "<=", (int) (b * L)).post();

    // total profit: sum of c[j] * X[j]
    int maxProfit = 0;
    for (int j = 0; j < n; j++) maxProfit += c[j] * u[j];
    IntVar totalProfit = m.intVar("total profit", 0, maxProfit, true);
    m.scalar(X, c, "=", totalProfit).post();

    // maximise the total profit
    m.setObjective(Model.MAXIMIZE, totalProfit);

    out.put("x", X);
    out.put("total_profit", totalProfit);
  }

  private static long lcm(long p, long q) {
    return p / gcd(p, q) * q;
  }

  private static long gcd(long p, long q) {
    return q == 0 ? p : gcd(q, p % q);
  }
}
