import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Sum the even-valued terms of the Fibonacci sequence that do not exceed four million.
// The sequence starts with 1 and 2, and each new term is the sum of the previous two terms.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // four million, the limit on the terms that are counted
    final int LIMIT = 4000000;
    // a bound on every term; no term of the first 33 is larger than this
    final int BIG = 10000000;
    // the first 33 terms; the terms after them are larger than four million and never count
    final int K = 33;

    CPIntVar limit = m.intVar(LIMIT, LIMIT);
    CPIntVar[] term = new CPIntVar[K];
    CPBoolVar[] odd = new CPBoolVar[K];
    CPBoolVar[] counted = new CPBoolVar[K];
    CPIntVar[] contrib = new CPIntVar[K];

    for (int i = 0; i < K; i++) {
      term[i] = m.intVar(1, BIG);
    }

    // the sequence starts with 1 and 2
    m.cp().post(eq(term[0], 1));
    m.cp().post(eq(term[1], 2));

    // each new term is the sum of the previous two terms
    for (int i = 2; i < K; i++) {
      m.cp().post(sum(new CPIntVar[]{term[i - 1], term[i - 2]}, term[i]));
    }

    for (int i = 0; i < K; i++) {
      // a term is twice a half plus a parity bit, so it is even exactly when the bit is 0
      CPIntVar half = m.intVar(0, BIG / 2);
      odd[i] = m.boolVar();
      m.cp().post(sum(new CPIntVar[]{mul(half, 2), odd[i]}, term[i]));

      // the term is counted when it is even and does not exceed four million
      CPBoolVar small = isLe(term[i], limit);
      counted[i] = m.boolVar();
      m.cp().post(implies(counted[i], not(odd[i])));
      m.cp().post(implies(counted[i], small));
      m.cp().post(or(new CPBoolVar[]{counted[i], odd[i], not(small)}));

      // the contribution is the term when it is counted, and zero otherwise
      contrib[i] = m.intVar(0, LIMIT);
      m.cp().post(ge(mul(counted[i], LIMIT), contrib[i]));
      m.cp().post(ge(term[i], contrib[i]));
      m.cp().post(ge(plus(contrib[i], BIG), sum(new CPIntVar[]{term[i], mul(counted[i], BIG)})));
    }

    // the sum of the even-valued terms that do not exceed four million
    out.put("res", sum(contrib));
  }
}
