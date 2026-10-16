import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Three coins lie on a table in the order tails, heads, tails.
// In precisely three moves make them face either all heads or all tails.
// Each move consists of choosing one coin and flipping it over.
// True means tails, False means heads.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] init = inst.getIntArray("init");
    int coins = init.length;
    int moves = inst.getInt("num_moves");

    // steps[t][c]: the state of coin c after t moves (row 0 is the table at the start)
    CPBoolVar[][] steps = new CPBoolVar[moves + 1][coins];
    for (int t = 0; t <= moves; t++) {
      steps[t] = m.boolVarArray(coins);
    }

    // the coins lie on the table in the order tails, heads, tails
    for (int c = 0; c < coins; c++) {
      m.cp().post(eq(steps[0][c], init[c]));
    }

    // each move consists of choosing one coin and flipping it over
    // (exactly one coin changes state between consecutive rows)
    int[][] flipRows = {{0, 0, 0}, {0, 1, 1}, {1, 0, 1}, {1, 1, 0}};
    for (int t = 0; t < moves; t++) {
      CPBoolVar[] flip = m.boolVarArray(coins);
      for (int c = 0; c < coins; c++) {
        // a coin is flipped exactly when its state before and after differ
        m.cp().post(table(new CPIntVar[]{steps[t][c], steps[t + 1][c], flip[c]}, flipRows));
      }
      // in each move exactly one coin is chosen
      m.cp().post(eq(sum(flip), 1));
    }

    // in the end make them face either all heads or all tails
    CPBoolVar[] last = steps[moves];
    for (int c = 1; c < coins; c++) {
      m.cp().post(eq(last[0], last[c]));
    }

    out.put("steps", steps);
  }
}
