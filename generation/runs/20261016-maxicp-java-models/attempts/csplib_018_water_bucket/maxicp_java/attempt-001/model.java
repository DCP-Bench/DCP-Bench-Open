// Water bucket problem: pour water between buckets with given capacities, starting
// from the initial fill, to reach the goal fill, minimising the number of transfers.
// sequence[0] is the initial state; sequence[t] is the state after the t-th transfer;
// after the goal is reached, the remaining entries are the padding state.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.List;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int steps = inst.getInt("MAX_STEPS");
    int pad = inst.getInt("PADDING_VALUE");
    int[] cap = inst.getIntArray("capacities");
    int[] init = inst.getIntArray("initial_state");
    int[] goal = inst.getIntArray("goal_state");
    int buckets = cap.length;
    int total = 0;
    for (int v : init) total += v;

    // state[t][k] is the water in bucket k after t transfers; padding is pad in every bucket
    CPIntVar[][] state = new CPIntVar[steps][buckets];
    for (int k = 0; k < buckets; k++)
      state[0][k] = m.intVar(init[k], init[k]);
    for (int t = 1; t < steps; t++)
      for (int k = 0; k < buckets; k++)
        state[t][k] = m.intVar(pad, cap[k]);

    // allowed transitions: a pour from one bucket into another fills the receiving
    // bucket up to its capacity or empties the pouring bucket, whichever comes first
    List<int[]> pours = new ArrayList<>();
    for (int a = 0; a <= cap[0]; a++)
      for (int b = 0; b <= cap[1]; b++)
        for (int c = 0; c <= cap[2]; c++) {
          if (a + b + c != total) continue;
          int[] s = {a, b, c};
          for (int i = 0; i < buckets; i++)
            for (int j = 0; j < buckets; j++) {
              if (i == j) continue;
              int amount = Math.min(s[i], cap[j] - s[j]);
              if (amount <= 0) continue;
              int[] n = s.clone();
              n[i] -= amount;
              n[j] += amount;
              int[] row = new int[2 * buckets];
              System.arraycopy(s, 0, row, 0, buckets);
              System.arraycopy(n, 0, row, buckets, buckets);
              pours.add(row);
            }
        }
    // the goal state may be followed by the padding state, and padding stays padding
    int[] goalPad = new int[2 * buckets];
    System.arraycopy(goal, 0, goalPad, 0, buckets);
    for (int k = 0; k < buckets; k++) goalPad[buckets + k] = pad;
    pours.add(goalPad);
    int[] padPad = new int[2 * buckets];
    for (int k = 0; k < 2 * buckets; k++) padPad[k] = pad;
    pours.add(padPad);
    int[][] rows = pours.toArray(new int[0][]);

    // each transfer pours water between two buckets, once the goal is reached the sequence is padded
    for (int t = 1; t < steps; t++) {
      CPIntVar[] pair = new CPIntVar[2 * buckets];
      for (int k = 0; k < buckets; k++) {
        pair[k] = state[t - 1][k];
        pair[buckets + k] = state[t][k];
      }
      m.cp().post(table(pair, rows));
    }

    // the sequence ends in the goal state (or in padding, if the goal was reached earlier)
    int[][] endRows = new int[2][buckets];
    for (int k = 0; k < buckets; k++) {
      endRows[0][k] = goal[k];
      endRows[1][k] = pad;
    }
    m.cp().post(table(state[steps - 1], endRows));

    // a transfer counts as a step when the state is not padding (the initial state is never padding)
    CPBoolVar[] transfers = new CPBoolVar[steps - 1];
    for (int t = 1; t < steps; t++)
      transfers[t - 1] = not(isEq(state[t][0], pad));

    // minimise the number of transfers between buckets to reach the goal
    CPIntVar cost = sum(transfers);
    m.minimize(cost);

    out.put("cost", cost);
    out.put("sequence", state);
  }
}
