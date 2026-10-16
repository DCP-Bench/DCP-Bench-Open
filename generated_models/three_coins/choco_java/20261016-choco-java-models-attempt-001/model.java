import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

// Three coins: three coins lie on a table as tails, heads, tails. In precisely
// three moves (each move flips one coin) make them all heads or all tails.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] init = inst.getIntArray("init");        // 1 = tails, 0 = heads
    int moves = inst.getInt("num_moves");
    int coins = init.length;

    // steps[t][c] = 1 if coin c shows tails after t moves (t = 0 is the start)
    BoolVar[][] steps = m.boolVarMatrix("steps", moves + 1, coins);

    // the coins lie on the table in the given order at the start
    for (int c = 0; c < coins; c++) m.arithm(steps[0][c], "=", init[c]).post();

    // each move flips exactly one coin: between consecutive states exactly one coin differs
    for (int t = 0; t < moves; t++) {
      BoolVar[] flipped = new BoolVar[coins];
      for (int c = 0; c < coins; c++)
        flipped[c] = m.arithm(steps[t][c], "!=", steps[t + 1][c]).reify();
      m.sum(flipped, "=", 1).post();
    }

    // at the end all coins face the same way: all heads or all tails
    for (int c = 1; c < coins; c++)
      m.arithm(steps[moves][0], "=", steps[moves][c]).post();

    out.put("steps", steps);
  }
}
