// Bowls and oranges: place m oranges in n bowls placed at positions 1..n, at most one
// orange per bowl, so that no three oranges A, B, C have dist(A,B) = dist(B,C).
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int k = inst.getInt("m");

    // bowl in which each orange sits, in ascending order (also one orange per bowl)
    IntVar[] x = m.intVarArray("x", k, 1, n);
    for (int i = 0; i + 1 < k; i++) {
      // the next orange is in a strictly later bowl
      m.arithm(x[i], "<", x[i + 1]).post();
    }

    // occ[p] = 1 if bowl p holds an orange
    IntVar[] occ = m.intVarArray("occ", n, 0, 1);
    for (int p = 1; p <= n; p++) {
      m.count(p, x, occ[p - 1]).post();
    }

    // no three bowls a, a+d, a+2d (equal spacing) all hold an orange
    for (int a = 1; a <= n; a++) {
      for (int d = 1; a + 2 * d <= n; d++) {
        // at most two of the three bowls with equal spacing hold an orange
        m.sum(new IntVar[]{occ[a - 1], occ[a + d - 1], occ[a + 2 * d - 1]}, "<=", 2).post();
      }
    }

    out.put("x", x);
  }
}
