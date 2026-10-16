// Ternary Steiner problem of order n: find n(n-1)/6 triples of elements from 1..n
// such that any two triples have at most one common element.
// sets[i][j] = true if element j is part of triple i.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int numTriples = n * (n - 1) / 6;

    // Each triple i also has three element variables elem[i][0..2] (the elements
    // of the triple in increasing order, 0-based). The order is only a way to
    // name the three elements of a set; it does not restrict the sets.
    CPIntVar[][] elem = new CPIntVar[numTriples][];
    // notIn[i][j] = 1 when element j is not in triple i; sets[i][j] = 1 - notIn[i][j]
    CPBoolVar[][] notIn = new CPBoolVar[numTriples][];
    CPIntVar[][] sets = new CPIntVar[numTriples][n];
    for (int i = 0; i < numTriples; i++) {
      elem[i] = m.intVarArray(3, 0, n - 1);
      m.cp().post(le(elem[i][0], minus(elem[i][1], 1)));
      m.cp().post(le(elem[i][1], minus(elem[i][2], 1)));
      notIn[i] = m.boolVarArray(n);
      for (int j = 0; j < n; j++) {
        sets[i][j] = plus(minus(notIn[i][j]), 1);
      }
    }

    // triple i holds element j exactly when one of its three elements is j
    for (int i = 0; i < numTriples; i++) {
      for (int j = 0; j < n; j++) {
        m.cp().post(eq(sum(new CPIntVar[] {isEq(elem[i][0], j), isEq(elem[i][1], j), isEq(elem[i][2], j)}), sets[i][j]));
      }
    }

    // every triple holds three elements
    for (int i = 0; i < numTriples; i++) {
      m.cp().post(eq(sum(sets[i]), 3));
    }

    // any two elements are together in at most one triple, and since the
    // triples cover 3 * n(n-1)/6 = n(n-1)/2 pairs, in exactly one triple.
    // (implied by the triple-intersection rule; stated for propagation)
    for (int a = 0; a < n; a++) {
      for (int b = a + 1; b < n; b++) {
        CPIntVar[] together = new CPIntVar[numTriples];
        for (int i = 0; i < numTriples; i++) {
          // together[i] = 1 exactly when elements a and b are both in triple i
          CPBoolVar t = m.boolVar();
          m.cp().post(le(sum(new CPIntVar[] {sets[i][a], sets[i][b], minus(t)}), 1));
          m.cp().post(le(sum(new CPIntVar[] {t, minus(sets[i][a])}), 0));
          m.cp().post(le(sum(new CPIntVar[] {t, minus(sets[i][b])}), 0));
          together[i] = t;
        }
        m.cp().post(eq(sum(together), 1));
      }
    }

    // each element lies in (n-1)/2 triples (implied by the pair condition)
    for (int j = 0; j < n; j++) {
      CPIntVar[] column = new CPIntVar[numTriples];
      for (int i = 0; i < numTriples; i++) {
        column[i] = sets[i][j];
      }
      m.cp().post(eq(sum(column), (n - 1) / 2));
    }

    out.put("sets", sets);
  }
}
