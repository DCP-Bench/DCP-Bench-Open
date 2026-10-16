import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Fibonacci even sum: the sum of all even-valued Fibonacci terms that do not exceed
// four million, with the sequence starting 1, 2.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // number of terms to generate: the sequence passes four million well before term 36
    int terms = 36;
    int limit = 4000000;
    // bound on any term; the last term 24157817 lies inside it
    int maxTerm = 30000000;

    IntVar[] t = m.intVarArray("t", terms, 1, maxTerm, true);

    // the sequence starts with 1 and 2
    m.arithm(t[0], "=", 1).post();
    m.arithm(t[1], "=", 2).post();

    // each new term is the sum of the previous two terms
    for (int k = 2; k < terms; k++) {
      m.arithm(t[k], "=", t[k - 1], "+", t[k - 2]).post();
    }

    // split each term into parity: term = 2 * half + parity; even when parity is 0
    IntVar[] half = m.intVarArray("half", terms, 0, maxTerm / 2, true);
    IntVar[] parity = m.intVarArray("parity", terms, 0, 1);
    for (int k = 0; k < terms; k++) {
      m.scalar(new IntVar[]{half[k], parity[k], t[k]}, new int[]{2, 1, -1}, "=", 0).post();
    }

    // the term does not exceed four million
    BoolVar[] notExceeds = new BoolVar[terms];
    for (int k = 0; k < terms; k++) {
      notExceeds[k] = t[k].le(limit).boolVar();
    }

    // the term is even: its parity is 0
    BoolVar[] even = new BoolVar[terms];
    for (int k = 0; k < terms; k++) {
      even[k] = m.isEq(parity[k], 0);
    }

    // a term counts when it is even and does not exceed four million
    IntVar[] counted = new IntVar[terms];
    for (int k = 0; k < terms; k++) {
      BoolVar both = m.boolVar("both" + k);
      m.times(notExceeds[k], even[k], both).post();
      counted[k] = m.intVar("counted" + k, 0, maxTerm, true);
      m.times(t[k], both, counted[k]).post();
    }

    // sum of the even-valued terms that do not exceed four million
    IntVar res = m.sum("res", counted);
    out.put("res", res);
  }
}
