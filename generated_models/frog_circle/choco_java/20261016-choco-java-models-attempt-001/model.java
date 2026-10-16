// Frog circle: arrange cards 1..n on a circle so that a frog starting on card 1 and jumping
// k places clockwise from each card k lands on every card.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // x[p] = the card at position p of the circle (positions 0..n-1, clockwise)
    IntVar[] x = m.intVarArray("x", n, 1, n);
    m.allDifferent(x, "AC").post();

    // nxt[p] = the position the frog reaches from position p: it jumps x[p] places clockwise
    IntVar[] nxt = m.intVarArray("nxt", n, 0, n - 1);
    for (int p = 0; p < n; p++) {
      // table[k-1] = position reached from p after jumping k places (k = card value, 1-based)
      int[] table = new int[n];
      for (int k = 1; k <= n; k++) table[k - 1] = (p + k) % n;
      m.element(nxt[p], table, x[p], 1).post();
    }

    // the frog starts on card 1, which is the first card of the arrangement (position 0)
    m.arithm(x[0], "=", 1).post();

    // pos[i] = position of the frog after i jumps; the walk visits every card, so its
    // first n positions are all different
    IntVar[] pos = m.intVarArray("pos", n, 0, n - 1);
    pos[0] = m.intVar(0);
    for (int i = 0; i + 1 < n; i++) {
      // pos[i+1] = nxt[pos[i]]: the frog jumps from the card it stands on
      m.element(pos[i + 1], nxt, pos[i], 0).post();
    }
    m.allDifferent(pos, "AC").post();

    out.put("x", x);
  }
}
