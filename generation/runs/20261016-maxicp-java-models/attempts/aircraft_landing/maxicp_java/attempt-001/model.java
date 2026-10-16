// Aircraft landing: one runway, a fixed landing sequence (plane i lands before plane j when i < j).
// Each plane lands inside its time window, close to its target time. Landing early costs
// penalty_before per time unit, landing late costs penalty_after per time unit. Consecutive
// planes need a minimum separation. Minimise the total penalty.
import static org.maxicp.cp.CPFactory.*;

import org.maxicp.cp.engine.core.CPIntVar;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] earliest = inst.getIntArray("earliest_landing");
    int[] latest = inst.getIntArray("latest_landing");
    int[] target = inst.getIntArray("target_landing");
    int[] penBefore = inst.getIntArray("penalty_before");
    int[] penAfter = inst.getIntArray("penalty_after");
    int[][] separation = inst.getIntMatrix("separation_time");
    int n = earliest.length;

    // the landing time of each aircraft, within its time window
    CPIntVar[] land = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      land[i] = m.intVar(earliest[i], latest[i]);
    }

    // landing time = target - early + late, where early and late are the time units
    // before and after the target. Each one is bounded by the window around its target.
    CPIntVar[] early = new CPIntVar[n];
    CPIntVar[] late = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      early[i] = m.intVar(0, Math.max(0, target[i] - earliest[i]));
      late[i] = m.intVar(0, Math.max(0, latest[i] - target[i]));
      // landing time is the target, minus the time landed early, plus the time landed late
      m.cp().post(eq(sum(land[i], early[i]), plus(late[i], target[i])));
    }

    // planes land in the fixed sequence, with the minimum separation between each pair
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        // plane j lands at least the separation time after plane i
        m.cp().post(ge(land[j], plus(land[i], separation[i][j])));
      }
    }

    // the penalty for landing early and for landing late, summed over all planes
    CPIntVar[] terms = new CPIntVar[2 * n];
    for (int i = 0; i < n; i++) {
      // penalty for landing early, per time unit before the target
      terms[2 * i] = mul(early[i], penBefore[i]);
      // penalty for landing late, per time unit after the target
      terms[2 * i + 1] = mul(late[i], penAfter[i]);
    }
    CPIntVar totalPenalty = sum(terms);
    // minimise the total penalty
    m.minimize(totalPenalty);

    out.put("landing_times", land);
    out.put("total_penalty", totalPenalty);
  }
}
