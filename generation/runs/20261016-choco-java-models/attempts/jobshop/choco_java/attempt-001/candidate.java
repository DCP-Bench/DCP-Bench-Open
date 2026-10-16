// Job shop scheduling: each job is a sequence of tasks, each task runs on a fixed machine,
// a machine processes one task at a time, and the goal is the smallest makespan.
// Instance data: jobs_data[j][k] = [machine, duration] of task k of job j (jobs may have different task counts).
import java.util.ArrayList;
import java.util.List;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.variables.Task;
import com.google.gson.JsonArray;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    JsonArray jobs = inst.raw("jobs_data").getAsJsonArray();
    int nj = jobs.size();
    int[][] machine = new int[nj][];
    int[][] dur = new int[nj][];
    int nMach = 0, horizon = 0;
    for (int j = 0; j < nj; j++) {
      JsonArray tasks = jobs.get(j).getAsJsonArray();
      machine[j] = new int[tasks.size()];
      dur[j] = new int[tasks.size()];
      for (int k = 0; k < tasks.size(); k++) {
        JsonArray pair = tasks.get(k).getAsJsonArray();
        machine[j][k] = pair.get(0).getAsInt();
        dur[j][k] = pair.get(1).getAsInt();
        nMach = Math.max(nMach, machine[j][k] + 1);
        horizon += dur[j][k];   // all tasks back to back bound the makespan
      }
    }

    // start time of every task
    IntVar[][] start = new IntVar[nj][];
    for (int j = 0; j < nj; j++) {
      start[j] = new IntVar[dur[j].length];
      for (int k = 0; k < dur[j].length; k++) {
        start[j][k] = m.intVar("start_" + j + "_" + k, 0, horizon, true);
      }
    }
    IntVar makespan = m.intVar("makespan", 0, horizon, true);

    // no task of a job starts before the previous task of that job is completed
    for (int j = 0; j < nj; j++) {
      for (int k = 1; k < dur[j].length; k++) {
        start[j][k - 1].add(dur[j][k - 1]).le(start[j][k]).post();
      }
    }

    // a machine can only work on one task at a time; a task runs to completion
    List<List<Task>> onMachine = new ArrayList<>();
    for (int mm = 0; mm < nMach; mm++) onMachine.add(new ArrayList<>());
    for (int j = 0; j < nj; j++) {
      for (int k = 0; k < dur[j].length; k++) {
        onMachine.get(machine[j][k]).add(m.taskVar(start[j][k], dur[j][k]));
      }
    }
    for (int mm = 0; mm < nMach; mm++) {
      List<Task> ts = onMachine.get(mm);
      if (ts.isEmpty()) continue;
      IntVar[] unit = new IntVar[ts.size()];
      for (int i = 0; i < unit.length; i++) unit[i] = m.intVar(1);
      m.cumulative(ts.toArray(new Task[0]), unit, m.intVar(1)).post();
    }

    // the makespan is the time the last task of every job completes
    for (int j = 0; j < nj; j++) {
      int last = dur[j].length - 1;
      start[j][last].add(dur[j][last]).le(makespan).post();
    }

    m.setObjective(Model.MINIMIZE, makespan);
    out.put("makespan", makespan);
  }
}
