import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

// Two disjoint non-empty subsets S and T of the set A of distinct integers, with
// equal sums. The sets need not cover A. Output membership flags for S and T.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] a = inst.getIntArray("A");
    int n = a.length;

    // in_S[i] = 1 if element i of A is in S; in_T[i] = 1 if it is in T
    BoolVar[] inS = m.boolVarArray("in_S", n);
    BoolVar[] inT = m.boolVarArray("in_T", n);

    // S and T are disjoint: no element is in both
    for (int i = 0; i < n; i++) {
      m.sum(new BoolVar[]{inS[i], inT[i]}, "<=", 1).post();
    }

    // the sum of the elements of S equals the sum of the elements of T
    BoolVar[] both = new BoolVar[2 * n];
    int[] weights = new int[2 * n];
    for (int i = 0; i < n; i++) {
      both[i] = inS[i];
      weights[i] = a[i];
      both[n + i] = inT[i];
      weights[n + i] = -a[i];
    }
    m.scalar(both, weights, "=", 0).post();

    // S and T are non-empty
    m.sum(inS, ">=", 1).post();
    m.sum(inT, ">=", 1).post();

    out.put("in_S", inS);
    out.put("in_T", inT);
  }
}
