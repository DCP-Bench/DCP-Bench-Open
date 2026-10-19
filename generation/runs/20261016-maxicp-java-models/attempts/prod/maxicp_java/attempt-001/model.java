import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Production problem: for each product j we choose a production quantity X[j]
// with 0 <= X[j] <= u[j]. Each unit of product j takes 1/a[j] units of the shared
// resource, and the total resource used must be at most b.
// The goal is to maximise the total profit, the sum of c[j] * X[j].
//
// The resource constraint has fractional coefficients 1/a[j]. To keep integer
// arithmetic, multiply it by L, the least common multiple of all a[j]:
// sum((L / a[j]) * X[j]) <= b * L.
public class Submission {

  private static long gcd(long p, long q) {
    return q == 0 ? p : gcd(q, p % q);
  }

  public static void build(Instance inst, Model m, Outputs out) {
    int[] a = inst.getIntArray("a");
    int[] c = inst.getIntArray("c");
    int[] u = inst.getIntArray("u");
    int b = inst.getInt("b");
    int n = a.length;

    // the least common multiple of the divisors a[j]
    long lcm = 1;
    for (int j = 0; j < n; j++) {
      lcm = lcm / gcd(lcm, a[j]) * a[j];
    }

    // the production quantity of each product, between 0 and its limit u[j]
    CPIntVar[] x = new CPIntVar[n];
    for (int j = 0; j < n; j++) {
      x[j] = m.intVar(0, u[j]);
    }

    // the resource used by all products is at most b
    CPIntVar[] usage = new CPIntVar[n];
    for (int j = 0; j < n; j++) {
      usage[j] = mul(x[j], (int) (lcm / a[j]));
    }
    m.cp().post(le(sum(usage), (int) (b * lcm)));

    // the total profit is the sum of c[j] * X[j]; its bounds follow from the bounds of X
    long lo = 0;
    long hi = 0;
    CPIntVar[] profit = new CPIntVar[n];
    for (int j = 0; j < n; j++) {
      profit[j] = mul(x[j], c[j]);
      long end = (long) c[j] * u[j];
      lo += Math.min(0, end);
      hi += Math.max(0, end);
    }
    CPIntVar total = m.intVar((int) lo, (int) hi);
    m.cp().post(eq(total, sum(profit)));
    m.maximize(total);

    out.put("total_profit", total);
    out.put("x", x);
  }
}
