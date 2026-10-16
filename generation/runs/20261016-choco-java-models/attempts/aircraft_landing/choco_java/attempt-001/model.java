// Aircraft landing: land n aircraft on one runway in a fixed order, each at a time
// within its window, with a minimum separation between any two landings, minimising
// the total penalty for landing early or late relative to each aircraft's target time.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] earliest = inst.getIntArray("earliest_landing");
    int[] latest = inst.getIntArray("latest_landing");
    int[] target = inst.getIntArray("target_landing");
    int[] penBefore = inst.getIntArray("penalty_before");
    int[] penAfter = inst.getIntArray("penalty_after");
    int[][] sep = inst.getIntMatrix("separation_time");
    int n = earliest.length;

    // largest possible gap between the target and the landing time, for the bounds
    int horizon = 0;
    for (int i = 0; i < n; i++) horizon = Math.max(horizon, latest[i]);

    // landing time of each aircraft, inside its window
    IntVar[] t = new IntVar[n];
    for (int i = 0; i < n; i++) t[i] = m.intVar("land_" + i, earliest[i], latest[i], true);

    // minimum separation between the landings of any two aircraft, in the fixed order
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        // aircraft j lands at least sep[i][j] after aircraft i
        m.arithm(t[j], "-", t[i], ">=", sep[i][j]).post();
      }
    }

    // earliness and lateness of each aircraft against its target landing time
    IntVar[] early = new IntVar[n];
    IntVar[] late = new IntVar[n];
    IntVar[] penVars = new IntVar[2 * n];
    int[] penCoef = new int[2 * n];
    for (int i = 0; i < n; i++) {
      early[i] = m.intVar("early_" + i, 0, horizon, true);
      late[i] = m.intVar("late_" + i, 0, horizon, true);
      // landing before the target: early is at least target minus landing time
      m.arithm(early[i], "+", t[i], ">=", target[i]).post();
      // landing after the target: late is at least landing time minus target
      m.arithm(late[i], "-", t[i], ">=", -target[i]).post();
      penVars[2 * i] = early[i];
      penCoef[2 * i] = penBefore[i];
      penVars[2 * i + 1] = late[i];
      penCoef[2 * i + 1] = penAfter[i];
    }

    // total penalty: penalty per minute early plus per minute late, over all aircraft
    long penUpper = 0;
    for (int i = 0; i < n; i++) penUpper += (long) horizon * (penBefore[i] + penAfter[i]);
    IntVar total = m.intVar("total_penalty", 0, (int) Math.min(penUpper, 21474836), true);
    m.scalar(penVars, penCoef, "=", total).post();
    m.setObjective(Model.MINIMIZE, total);

    out.put("landing_times", t);
    out.put("total_penalty", total);
  }
}
