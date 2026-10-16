import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Cards numbered 1 to n are arranged in a circle. A frog jumps on card 1, then
// jumps to the card 1 place clockwise; from card k it jumps k places clockwise.
// Find an arrangement of the cards that lets the frog jump on every card.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");

    // print the card arrangement x: a list of n different integers from 1 to n
    CPIntVar[] x = m.intVarArray(n, 1, n);
    m.cp().post(allDifferent(x));

    // the frog starts on card 1, which is the first card of the arrangement
    m.cp().post(eq(x[0], 1));

    // the frog is on place p at its t-th jump; it visits one place per jump
    CPBoolVar[][] at = new CPBoolVar[n][];
    for (int t = 0; t < n; t++) at[t] = m.boolVarArray(n);
    for (int t = 0; t < n; t++) {
      // the frog is on exactly one card at each jump
      m.cp().post(eq(sum(at[t]), 1));
    }
    for (int p = 0; p < n; p++) {
      // the frog jumps on every card, so each place is visited once
      CPBoolVar[] visits = new CPBoolVar[n];
      for (int t = 0; t < n; t++) visits[t] = at[t][p];
      m.cp().post(eq(sum(visits), 1));
    }

    // the frog starts on card 1
    for (int p = 0; p < n; p++) {
      // the first jump is from the place holding card 1
      m.cp().post(eq(at[0][p], isEq(x[p], 1)));
    }

    // from card k the frog jumps k places clockwise
    for (int t = 0; t + 1 < n; t++) {
      for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
          // the jump length from place i to place j is the card on place i
          int k = ((j - i) % n + n) % n;
          if (k == 0) k = n;
          // if the frog is on place i then on place j next, card i must be k
          m.cp().post(or(new CPBoolVar[] {not(at[t][i]), not(at[t + 1][j]), isEq(x[i], k)}));
        }
      }
    }

    out.put("x", x);
  }
}
