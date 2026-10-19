import org.maxicp.cp.engine.constraints.scheduling.CPCumulFunction;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPIntervalVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Resource-constrained project scheduling: give each job a start time so that
// jobs wait for their predecessors, no resource exceeds its capacity at any time,
// and the project duration (makespan) is as small as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] dur = inst.getIntArray("durations_data");
    int[][] need = inst.getIntMatrix("resource_needs_data");
    int[] cap = inst.getIntArray("resource_capacities_data");
    int[][] succ = inst.getIntMatrix("successors_link_data");
    int n = dur.length;
    int numRes = cap.length;

    // the jobs run one after another in any order, so the sum of durations bounds every start time
    int horizon = 0;
    for (int d : dur) horizon += d;
    if (horizon < 1) horizon = 1;

    var cp = m.cp();

    // each job is a task that must run for its duration
    CPIntervalVar[] task = new CPIntervalVar[n];
    for (int i = 0; i < n; i++) task[i] = makeIntervalVar(cp, false, dur[i]);
    for (int i = 0; i < n; i++) cp.post(le(start(task[i]), horizon));

    // a job can only start once every job that precedes it is finished
    for (int[] link : succ) {
      cp.post(endBeforeStart(task[link[0]], task[link[1]]));
    }

    // the jobs using each resource stay within its capacity at every time point
    for (int r = 0; r < numRes; r++) {
      int totalNeed = 0;
      for (int i = 0; i < n; i++) totalNeed += need[i][r];
      if (totalNeed <= cap[r]) continue;
      java.util.List<CPCumulFunction> pulses = new java.util.ArrayList<>();
      for (int i = 0; i < n; i++) {
        if (dur[i] > 0 && need[i][r] > 0) pulses.add(pulse(task[i], need[i][r]));
      }
      if (pulses.isEmpty()) continue;
      cp.post(le(sum(pulses.toArray(new CPCumulFunction[0])), cap[r]));
    }

    // the project duration is the time the last job ends
    m.minimize(makespan(task));

    // the reported start time of each job
    CPIntVar[] startTime = new CPIntVar[n];
    for (int i = 0; i < n; i++) startTime[i] = start(task[i]);
    out.put("start_time", startTime);
  }
}
