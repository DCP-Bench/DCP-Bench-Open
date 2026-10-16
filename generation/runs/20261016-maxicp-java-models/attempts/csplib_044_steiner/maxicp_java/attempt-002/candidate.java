// Ternary Steiner problem of order n: find n(n-1)/6 triples of distinct elements from 1..n
// such that any two triples have at most one common element.
// sets[i][j] = true if element j is part of triple i (0-based elements, 0..n-1).
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
    int r = (n - 1) / 2; // number of triples through each element

    // the three elements of triple i, in increasing order; these are the decisions the search branches on,
    // and small values come first, so the search builds triples from the low elements up
    CPIntVar[][] elem = new CPIntVar[numTriples][];
    for (int i = 0; i < numTriples; i++) {
      elem[i] = m.intVarArray(3, 0, n - 1);
      // a triple holds three distinct elements, listed in increasing order
      m.cp().post(le(elem[i][0], minus(elem[i][1], 1)));
      m.cp().post(le(elem[i][1], minus(elem[i][2], 1)));
    }

    // the triples are listed by their smallest element
    for (int i = 0; i + 1 < numTriples; i++) {
      m.cp().post(le(elem[i][0], elem[i + 1][0]));
    }

    // sets[i][j] = 1 exactly when element j is one of the three elements of triple i
    CPBoolVar[][] sets = new CPBoolVar[numTriples][n];
    for (int i = 0; i < numTriples; i++) {
      for (int j = 0; j < n; j++) {
        sets[i][j] = makeBoolVar(m.cp());
        m.cp().post(eq(sum(new CPIntVar[] {isEq(elem[i][0], j), isEq(elem[i][1], j), isEq(elem[i][2], j)}), sets[i][j]));
      }
    }

    // every triple holds three elements (implied by the element variables; stated for propagation)
    for (int i = 0; i < numTriples; i++) {
      m.cp().post(sum(sets[i], 3));
    }

    // every element lies in (n-1)/2 triples (each triple through it covers two of the other n-1 elements)
    for (int j = 0; j < n; j++) {
      CPIntVar[] column = new CPIntVar[numTriples];
      for (int i = 0; i < numTriples; i++) {
        column[i] = sets[i][j];
      }
      m.cp().post(sum(column, r));
    }

    // any two elements are together in at most one triple; there are n(n-1)/2 pairs and
    // the triples cover 3 * n(n-1)/6 = n(n-1)/2 of them, so each pair is in exactly one triple
    for (int a = 0; a < n; a++) {
      for (int b = a + 1; b < n; b++) {
        // both[i] = 1 exactly when elements a and b are both in triple i
        CPBoolVar[] both = new CPBoolVar[numTriples];
        for (int i = 0; i < numTriples; i++) {
          CPBoolVar t = makeBoolVar(m.cp());
          m.cp().post(le(t, sets[i][a]));
          m.cp().post(le(t, sets[i][b]));
          m.cp().post(le(sum(new CPIntVar[] {sets[i][a], sets[i][b], minus(t)}), 1));
          both[i] = t;
        }
        m.cp().post(sum(both, 1));
      }
    }

    // symmetry breaking, valid by relabelling the elements 1..n-1: the r triples through
    // element 0 are disjoint apart from 0, so they can be named {0,1,2}, {0,3,4}, ...
    // (they come first in the listing, since they have the smallest element 0)
    for (int i = 0; i < r; i++) {
      m.cp().post(eq(elem[i][0], 0));
      m.cp().post(eq(elem[i][1], 2 * i + 1));
      m.cp().post(eq(elem[i][2], 2 * i + 2));
    }

    out.put("sets", sets);
  }
}
