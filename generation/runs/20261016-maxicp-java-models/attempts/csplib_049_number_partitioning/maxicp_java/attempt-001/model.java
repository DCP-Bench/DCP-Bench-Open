import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Number partitioning (CSPlib 049): split the numbers 1..n into two sets A and B
// such that A and B have the same cardinality, the same sum, and the same sum of
// squares. Output A and B, each listed in ascending order.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int half = n / 2;

    // x[i-1] = 1 if the number i is in A, 0 if it is in B
    CPBoolVar[] x = m.boolVarArray(n);

    // A and B have the same cardinality: 2 * |A| = n (no solution for odd n)
    m.cp().post(eq(mul(sum(x), 2), n));

    // Output sets: A holds the numbers with x = 1, B the numbers with x = 0,
    // each as an ascending list of `half` values
    CPIntVar[] a = m.intVarArray(half, 1, n);
    CPIntVar[] b = m.intVarArray(half, 1, n);
    for (int k = 0; k + 1 < half; k++) {
      // the elements of A are listed in ascending order, with no repeats
      m.cp().post(ge(a[k + 1], plus(a[k], 1)));
      // the elements of B are listed in ascending order, with no repeats
      m.cp().post(ge(b[k + 1], plus(b[k], 1)));
    }

    // every number is in A exactly when it is listed in A
    for (int i = 1; i <= n; i++) {
      CPBoolVar[] listed = new CPBoolVar[half];
      for (int k = 0; k < half; k++) listed[k] = isEq(a[k], i);
      m.cp().post(eq(sum(listed), x[i - 1]));
    }
    // every number is in B exactly when it is listed in B (the complement of A)
    for (int i = 1; i <= n; i++) {
      CPBoolVar[] listed = new CPBoolVar[half];
      for (int k = 0; k < half; k++) listed[k] = isEq(b[k], i);
      m.cp().post(eq(sum(listed), not(x[i - 1])));
    }

    // A and B have the same sum: sum of A - sum of B = 0,
    // written as 2 * (sum of A) = total of 1..n
    int total = n * (n + 1) / 2;
    CPIntVar[] sumTerms = new CPIntVar[n];
    for (int i = 1; i <= n; i++) sumTerms[i - 1] = mul(x[i - 1], 2 * i);
    m.cp().post(eq(sum(sumTerms), total));

    // A and B have the same sum of squares: 2 * (sum of squares in A) = sum of squares of 1..n
    int totalSq = n * (n + 1) * (2 * n + 1) / 6;
    CPIntVar[] sqTerms = new CPIntVar[n];
    for (int i = 1; i <= n; i++) sqTerms[i - 1] = mul(x[i - 1], 2 * i * i);
    m.cp().post(eq(sum(sqTerms), totalSq));

    out.put("A", a);
    out.put("B", b);
  }
}
