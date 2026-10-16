import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPIntervalVar;
import org.maxicp.cp.engine.core.CPSolver;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Job shop: several jobs, each a sequence of tasks, each task on a given machine for a given time.
// The tasks of a job run in their given order, a machine works on one task at a time,
// and a task once started runs to completion.
// Minimise the makespan, the time at which all jobs are completed.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // jobs_data[j][t] = {machine, duration} of task t of job j
    int[][][] jobs = inst.getInt3("jobs_data");
    int nJobs = jobs.length;

    // the horizon is the total processing time, which bounds every start and the makespan
    int horizon = 0;
    for (int[][] job : jobs)
      for (int[] task : job) horizon += task[1];

    CPSolver cp = m.cp();

    // one interval per task, which must run, and one decision variable for its start time
    CPIntervalVar[][] iv = new CPIntervalVar[nJobs][];
    CPIntVar[][] startVar = new CPIntVar[nJobs][];
    for (int j = 0; j < nJobs; j++) {
      iv[j] = new CPIntervalVar[jobs[j].length];
      startVar[j] = new CPIntVar[jobs[j].length];
      for (int t = 0; t < jobs[j].length; t++) {
        int d = jobs[j][t][1];
        iv[j][t] = makeIntervalVar(cp, false, d);
        startVar[j][t] = m.intVar(0, horizon);
        // the start time of the task is the decision variable
        cp.post(eq(start(iv[j][t]), startVar[j][t]));
      }
    }

    // the tasks of a job must be performed in the given order:
    // no task for a job can be started until the previous task for that job is completed
    for (int j = 0; j < nJobs; j++)
      for (int t = 0; t + 1 < jobs[j].length; t++)
        cp.post(endBeforeStart(iv[j][t], iv[j][t + 1]));

    // a machine can only work on one task at a time
    int maxMachine = -1;
    for (int[][] job : jobs)
      for (int[] task : job) maxMachine = Math.max(maxMachine, task[0]);
    for (int k = 0; k <= maxMachine; k++) {
      int count = 0;
      for (int[][] job : jobs)
        for (int[] task : job) if (task[0] == k) count++;
      if (count == 0) continue;
      CPIntervalVar[] onMachine = new CPIntervalVar[count];
      int c = 0;
      for (int j = 0; j < nJobs; j++)
        for (int t = 0; t < jobs[j].length; t++)
          if (jobs[j][t][0] == k) onMachine[c++] = iv[j][t];
      cp.post(noOverlap(onMachine));
    }

    // the makespan is the time at which the last task is completed
    CPIntVar all = makespan(flatten(iv));
    CPIntVar obj = m.intVar(0, horizon);
    cp.post(eq(obj, all));
    m.minimize(obj);

    out.put("makespan", obj);
  }

  private static CPIntervalVar[] flatten(CPIntervalVar[][] iv) {
    int n = 0;
    for (CPIntervalVar[] row : iv) n += row.length;
    CPIntervalVar[] r = new CPIntervalVar[n];
    int c = 0;
    for (CPIntervalVar[] row : iv)
      for (CPIntervalVar v : row) r[c++] = v;
    return r;
  }
}
