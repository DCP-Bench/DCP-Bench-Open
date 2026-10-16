import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Smallest a at least min_a such that a - b is prime and a * b is a perfect square n * n,
// for some positive b. Values a, b, n and the prime p are bounded by max_val.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int minA = inst.getInt("min_a");
    int maxVal = inst.getInt("max_val");

    IntVar a = m.intVar("a", minA, maxVal, true);      // the value to minimise, at least min_a
    IntVar b = m.intVar("b", 1, maxVal, true);         // b is positive
    IntVar p = m.intVar("p", primesUpTo(maxVal));      // a - b is prime
    IntVar n = m.intVar("n", 1, maxVal, true);         // n is the square root of a * b
    IntVar square = m.intVar("square", 1, maxVal * maxVal, true);  // a * b, at most max_val squared

    // a - b is the prime p
    m.sum(new IntVar[]{b, p}, "=", a).post();

    // a * b is the perfect square n * n
    m.times(a, b, square).post();
    m.times(n, n, square).post();

    m.setObjective(Model.MINIMIZE, a);

    out.put("a", a);
    out.put("b", b);
    out.put("n", n);
    out.put("p", p);
  }

  // All primes from 2 to limit, found by a sieve. Used only to give p its domain.
  static int[] primesUpTo(int limit) {
    boolean[] composite = new boolean[limit + 1];
    int count = 0;
    for (int i = 2; i <= limit; i++) {
      if (composite[i]) continue;
      count++;
      for (long j = (long) i * i; j <= limit; j += i) composite[(int) j] = true;
    }
    int[] primes = new int[count];
    int k = 0;
    for (int i = 2; i <= limit; i++) if (!composite[i]) primes[k++] = i;
    return primes;
  }
}
