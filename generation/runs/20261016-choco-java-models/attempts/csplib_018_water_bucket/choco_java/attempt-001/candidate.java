import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Water bucket: three buckets of capacities 8, 5 and 3 start with 8, 0 and 0 pints.
// Pour water between buckets until the 8 pint and 5 pint buckets hold 4 pints each,
// with the minimum number of transfers. The sequence lists the states, one per step,
// and is padded with the padding state after the goal.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] cap = inst.getIntArray("capacities");
    int[] init = inst.getIntArray("initial_state");
    int[] goal = inst.getIntArray("goal_state");
    int steps = inst.getInt("MAX_STEPS");
    int pad = inst.getInt("PADDING_VALUE");

    // state[t][b]: pints in bucket b after t transfers, or the padding value after the goal
    IntVar[][] state = m.intVarMatrix("state", steps, 3, pad, 8);
    for (int t = 0; t < steps; t++)
      for (int b = 0; b < 3; b++)
        m.arithm(state[t][b], "<=", cap[b]).post();

    // the first state is the initial state
    for (int b = 0; b < 3; b++) m.arithm(state[0][b], "=", init[b]).post();

    // every step is a legal pour from one bucket into another, pouring until the
    // receiving bucket is full or the pouring bucket is empty; once the goal is
    // reached, only padding follows
    Tuples step = new Tuples(true);
    for (int a = 0; a <= cap[0]; a++)
      for (int b = 0; b <= cap[1]; b++)
        for (int c = 0; c <= cap[2]; c++) {
          int[] from = {a, b, c};
          for (int i = 0; i < 3; i++)
            for (int j = 0; j < 3; j++) {
              if (i == j) continue;
              int amount = Math.min(from[i], cap[j] - from[j]);
              if (amount <= 0) continue;
              int[] to = from.clone();
              to[i] -= amount;
              to[j] += amount;
              step.add(a, b, c, to[0], to[1], to[2]);
            }
        }
    step.add(goal[0], goal[1], goal[2], pad, pad, pad);  // the goal is followed by padding
    step.add(pad, pad, pad, pad, pad, pad);             // padding is followed by padding
    for (int t = 0; t + 1 < steps; t++) {
      IntVar[] pair = new IntVar[6];
      for (int b = 0; b < 3; b++) { pair[b] = state[t][b]; pair[3 + b] = state[t + 1][b]; }
      m.table(pair, step).post();
    }

    // the sequence ends at the goal (or padding if the goal came earlier)
    Tuples end = new Tuples(true);
    end.add(goal[0], goal[1], goal[2]);
    end.add(pad, pad, pad);
    m.table(state[steps - 1], end).post();

    // the number of transfers: every state after the first that is not padding
    BoolVar[] transfer = new BoolVar[steps - 1];
    for (int t = 1; t < steps; t++)
      transfer[t - 1] = m.arithm(state[t][0], "!=", pad).reify();
    IntVar cost = m.intVar("cost", 0, steps - 1, true);
    m.sum(transfer, "=", cost).post();
    m.setObjective(Model.MINIMIZE, cost);

    out.put("cost", cost);
    out.put("sequence", state);
  }
}
