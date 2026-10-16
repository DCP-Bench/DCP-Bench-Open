import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Resource-constrained project scheduling: give each job a start time so that
// every precedence holds, no resource is over its capacity at any time, and the
// project duration (makespan) is as small as possible.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] dur = inst.getIntArray("durations_data");
    int[][] need = inst.getIntMatrix("resource_needs_data");
    int[] cap = inst.getIntArray("resource_capacities_data");
    int[][] succ = inst.getIntMatrix("successors_link_data");
    int n = dur.length;
    int numRes = cap.length;

    // the jobs run one after another in any feasible-by-precedence order, so the sum of durations bounds every start time
    int horizon = 0;
    for (int d : dur) horizon += d;
    if (horizon < 1) horizon = 1;

    var cp = m.cp();

    // constant variables used as time points
    CPIntVar[] at = new CPIntVar[horizon + 1];
    for (int t = 0; t <= horizon; t++) at[t] = makeIntVar(cp, t, t);

    // one start time per job
    CPIntVar[] start = m.intVarArray(n, 0, horizon);

    // a job starts only after the jobs that precede it have finished
    for (int[] link : succ) {
      int a = link[0];
      int b = link[1];
      cp.post(ge(start[b], plus(start[a], dur[a])));
    }

    // the project duration is at least the finishing time of every job
    CPIntVar makespan = m.intVar(0, horizon);
    for (int i = 0; i < n; i++) {
      cp.post(le(plus(start[i], dur[i]), makespan));
    }
    m.minimize(makespan);

    // job i is running at time t when it started at or before t and has not finished before t
    CPBoolVar[][] running = new CPBoolVar[n][horizon];
    for (int i = 0; i < n; i++) {
      if (dur[i] == 0) continue;
      for (int t = 0; t < horizon; t++) {
        CPBoolVar run = makeBoolVar(cp);
        running[i][t] = run;
        CPBoolVar startedByT = isLe(start[i], at[t]);
        if (t - dur[i] >= 0) {
          // a job that started at or before t - d has finished by t
          CPBoolVar startedByBefore = isLe(start[i], at[t - dur[i]]);
          cp.post(or(new CPBoolVar[] {not(run), startedByT}));
          cp.post(or(new CPBoolVar[] {not(run), not(startedByBefore)}));
          cp.post(or(new CPBoolVar[] {not(startedByT), startedByBefore, run}));
        } else {
          // a job that starts at or before t has not finished before t
          cp.post(or(new CPBoolVar[] {not(run), startedByT}));
          cp.post(or(new CPBoolVar[] {not(startedByT), run}));
        }
      }
    }

    // at every time, the needs of the running jobs stay within each resource capacity
    for (int r = 0; r < numRes; r++) {
      int totalNeed = 0;
      for (int i = 0; i < n; i++) totalNeed += need[i][r];
      if (totalNeed <= cap[r]) continue;
      for (int t = 0; t < horizon; t++) {
        List<CPIntVar> terms = new ArrayList<>();
        for (int i = 0; i < n; i++) {
          if (running[i][t] != null && need[i][r] > 0) {
            terms.add(mul(running[i][t], need[i][r]));
          }
        }
        if (!terms.isEmpty()) {
          cp.post(le(sum(terms.toArray(new CPIntVar[0])), cap[r]));
        }
      }
    }

    out.put("start_time", start);
  }
}
