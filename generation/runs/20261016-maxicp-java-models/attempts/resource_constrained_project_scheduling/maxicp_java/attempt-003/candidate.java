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

    // the longest chain of jobs from the start: head[i] is the earliest start of job i by precedences alone
    int[] head = new int[n];
    for (int pass = 0; pass < n; pass++) {
      for (int[] link : succ) {
        int a = link[0];
        int b = link[1];
        head[b] = Math.max(head[b], head[a] + dur[a]);
      }
    }
    // after[i] is the longest chain of work that must follow job i once it has finished
    int[] after = new int[n];
    for (int pass = 0; pass < n; pass++) {
      for (int[] link : succ) {
        int a = link[0];
        int b = link[1];
        after[a] = Math.max(after[a], dur[b] + after[b]);
      }
    }
    // the project cannot finish before the longest precedence chain
    int lowerBound = 0;
    for (int i = 0; i < n; i++) lowerBound = Math.max(lowerBound, head[i] + dur[i]);
    // the project cannot finish before the work of each resource fits its capacity
    for (int r = 0; r < numRes; r++) {
      long work = 0;
      for (int i = 0; i < n; i++) work += (long) dur[i] * need[i][r];
      if (cap[r] > 0) lowerBound = Math.max(lowerBound, (int) ((work + cap[r] - 1) / cap[r]));
    }

    var cp = m.cp();

    // each job is a task that must run for its duration
    CPIntervalVar[] task = new CPIntervalVar[n];
    for (int i = 0; i < n; i++) task[i] = makeIntervalVar(cp, false, dur[i]);
    for (int i = 0; i < n; i++) {
      // a job cannot start before the jobs that precede it can be finished
      if (head[i] > 0) cp.post(startAfter(task[i], head[i]));
      // every job starts within the time horizon
      cp.post(le(start(task[i]), horizon));
    }

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

    // the project duration is the time the last job ends, and it is at least the lower bound
    CPIntVar makespan = makespan(task);
    cp.post(ge(makespan, lowerBound));
    // a job and the chain of jobs that follow it end before the project does
    for (int i = 0; i < n; i++) {
      cp.post(le(plus(start(task[i]), dur[i] + after[i]), makespan));
    }
    m.minimize(makespan);

    // the reported start time of each job
    CPIntVar[] startTime = new CPIntVar[n];
    for (int i = 0; i < n; i++) startTime[i] = start(task[i]);
    out.put("start_time", startTime);
  }
}
