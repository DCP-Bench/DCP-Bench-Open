import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Number partitioning: split the numbers 1..n into two sets A and B of equal size,
// with equal sums and equal sums of squares.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int h = n / 2;

    // a[k] is the k-th smallest element of A, b[k] of B
    IntVar[] a = m.intVarArray("A", h, 1, n);
    IntVar[] b = m.intVarArray("B", h, 1, n);

    // A and B together are exactly the numbers 1..n, each used once
    IntVar[] all = new IntVar[n];
    for (int k = 0; k < h; k++) {
      all[k] = a[k];
      all[h + k] = b[k];
    }
    m.allDifferent(all, "AC").post();

    // the elements of each set are listed in increasing order
    m.increasing(a, 1).post();
    m.increasing(b, 1).post();

    // the total of 1..n is fixed by the data; the sums of A and B are then forced equal,
    // so an odd total has no solution
    int total = n * (n + 1) / 2;
    m.sum(all, "=", total).post();

    // sum of the numbers in A equals sum of the numbers in B
    IntVar sumA = m.sum("sumA", a);
    IntVar sumB = m.sum("sumB", b);
    m.arithm(sumA, "=", sumB).post();

    // sum of the squares in A equals sum of the squares in B
    IntVar[] squaresA = m.intVarArray("squareA", h, 1, n * n, true);
    IntVar[] squaresB = m.intVarArray("squareB", h, 1, n * n, true);
    for (int k = 0; k < h; k++) {
      m.square(squaresA[k], a[k]).post();
      m.square(squaresB[k], b[k]).post();
    }
    IntVar sqA = m.sum("sumSquaresA", squaresA);
    IntVar sqB = m.sum("sumSquaresB", squaresB);
    m.arithm(sqA, "=", sqB).post();

    out.put("A", a);
    out.put("B", b);
  }
}
