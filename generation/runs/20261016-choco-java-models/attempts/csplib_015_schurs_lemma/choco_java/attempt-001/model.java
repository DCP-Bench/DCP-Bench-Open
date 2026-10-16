import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Schur's lemma: put balls 1..n into c boxes so that no triple (x, y, z) with x + y = z
// has all three balls in the same box.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int c = inst.getInt("c");

    // M[i][j] is true when ball i+1 is in box j+1
    BoolVar[][] M = m.boolVarMatrix("M", n, c);

    // a ball must be in exactly one box: M_i1 + M_i2 + M_i3 = 1
    for (int i = 0; i < n; i++) {
      m.sum(M[i], "=", 1).post();
    }

    // for any triple x + y = z and any box j, not all three balls are in box j:
    // M_xj + M_yj + M_zj <= 2
    for (int x = 1; x <= n; x++) {
      for (int y = x; x + y <= n; y++) {
        int z = x + y;
        for (int j = 0; j < c; j++) {
          m.sum(new BoolVar[]{M[x - 1][j], M[y - 1][j], M[z - 1][j]}, "<=", 2).post();
        }
      }
    }

    // the box of each ball, numbered 1 to c
    IntVar[] balls = new IntVar[n];
    for (int i = 0; i < n; i++) {
      int[] weights = new int[c];
      for (int j = 0; j < c; j++) weights[j] = j + 1;
      balls[i] = m.intVar("balls" + (i + 1), 1, c);
      m.scalar(M[i], weights, "=", balls[i]).post();
    }

    out.put("balls", balls);
  }
}
