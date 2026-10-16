import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Given a set A of different integers, find two disjoint non-empty subsets S and T of A
// whose elements sum to the same value.
// in_S[i] = 1 if A[i] is in S, in_T[i] = 1 if A[i] is in T.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] a = inst.getIntArray("A");
    int n = a.length;

    // the elements of A that are in S, and the elements of A that are in T
    CPBoolVar[] inS = m.boolVarArray(n);
    CPBoolVar[] inT = m.boolVarArray(n);

    // S and T are disjoint: no element of A is in both
    for (int i = 0; i < n; i++) {
      m.cp().post(le(sum(inS[i], inT[i]), 1));
    }

    // S is non-empty
    m.cp().post(ge(sum(inS), 1));
    // T is non-empty
    m.cp().post(ge(sum(inT), 1));

    // the sum of the elements in S equals the sum of the elements in T
    CPIntVar[] valS = new CPIntVar[n];
    CPIntVar[] valT = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      valS[i] = mul(inS[i], a[i]);
      valT[i] = mul(inT[i], a[i]);
    }
    m.cp().post(eq(sum(valS), sum(valT)));

    out.put("in_S", inS);
    out.put("in_T", inT);
  }
}
