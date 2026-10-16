// Find the smallest a, no less than min_a, for which there are positive integers
// b, n, p with a - b = p, p a prime number, and a * b = n^2 (a perfect square).
//
// Derivation used to make the search small. Write a = s*u^2 and b = s*v^2, where s is
// the squarefree part shared by a and b (a * b is a square exactly when a and b have the
// same squarefree part). Then p = a - b = s*(u^2 - v^2). Since p is prime, s is 1 or p.
// s = p would give u^2 - v^2 = 1, so v = 0 and b = 0, which is excluded. So s = 1 and
// (u - v)(u + v) = p, which forces u - v = 1 and u + v = p. Hence
//   a = u^2,  b = (u - 1)^2,  n = u(u - 1),  p = 2u - 1,
// and the search only chooses u, with 2u - 1 prime. The description's constraints still
// hold by construction, and the prime test below is posted on p.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int minA = inst.getInt("min_a");
    int maxVal = inst.getInt("max_val");

    // u is the only decision: a = u^2 must lie in [min_a, max_val], and b = (u - 1)^2 > 0 needs u >= 2
    int lo = 2;
    while ((long) lo * lo < minA) lo++;
    int hi = 2;
    while ((long) (hi + 1) * (hi + 1) <= maxVal) hi++;
    CPIntVar u = m.intVar(lo, Math.max(lo, hi));
    if (lo > hi) m.cp().post(le(u, hi)); // no u fits the bounds: refuted at the root, so no solution

    // a = u^2, the smallest value sought
    CPIntVar a = mul(u, u);
    // v = u - 1, so b = v^2 is a positive integer
    CPIntVar v = minus(u, 1);
    // b = (u - 1)^2
    CPIntVar b = mul(v, v);
    // n = u(u - 1), the root of a * b = n^2
    CPIntVar n = mul(u, v);
    // p = a - b = 2u - 1, a prime number
    CPIntVar p = sum(new CPIntVar[]{a, minus(b)});

    // p must be prime: exclude every value in 2..max_val that is not prime (trial division)
    for (int k = 2; k <= maxVal; k++) {
      boolean prime = true;
      for (int d = 2; (long) d * d <= k; d++) {
        if (k % d == 0) { prime = false; break; }
      }
      if (!prime) m.cp().post(neq(p, k));
    }

    // minimise a
    m.minimize(a);

    out.put("a", a);
    out.put("b", b);
    out.put("n", n);
    out.put("p", p);
  }
}
