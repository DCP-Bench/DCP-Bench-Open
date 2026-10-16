import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Permutation flow shop: every job visits the machines in the same order 1..M, and a machine
// works on one job at a time. Choose the sequence of jobs that minimises the makespan, the time
// when the last job leaves the last machine.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // processTime[j][k]: time job j needs on machine k (rows are the jobs, columns the machines)
    int[][] processTime = inst.getIntMatrix("process_time");
    int n = processTime.length;
    int machines = processTime[0].length;

    // the sum of all processing times bounds every completion time
    int horizon = 0;
    for (int[] row : processTime) for (int t : row) horizon += t;

    // position[p]: the job placed at position p of the sequence
    CPIntVar[] position = m.intVarArray(n, 0, n - 1);
    // the sequence visits every job exactly once
    m.cp().post(allDifferent(position));

    // duration[p][k]: processing time of the job at position p on machine k
    CPIntVar[][] duration = new CPIntVar[n][machines];
    for (int k = 0; k < machines; k++) {
      int[] column = new int[n];
      for (int j = 0; j < n; j++) column[j] = processTime[j][k];
      for (int p = 0; p < n; p++) duration[p][k] = element(column, position[p]);
    }

    // completion[p][k]: time the job at position p leaves machine k
    CPIntVar[][] completion = new CPIntVar[n][machines];
    for (int p = 0; p < n; p++) {
      for (int k = 0; k < machines; k++) {
        completion[p][k] = makeIntVar(m.cp(), 0, horizon);
      }
    }
    for (int p = 0; p < n; p++) {
      for (int k = 0; k < machines; k++) {
        // a job starts on a machine when the job before it in the sequence has left that machine
        // and the same job has left the previous machine: the later of the two
        CPIntVar before = p > 0 ? completion[p - 1][k] : null;
        CPIntVar previous = k > 0 ? completion[p][k - 1] : null;
        // the job leaves the machine once its processing time has elapsed after its start
        if (before == null && previous == null) {
          // first job on the first machine starts at time 0
          m.cp().post(eq(completion[p][k], duration[p][k]));
        } else if (before == null) {
          m.cp().post(sum(new CPIntVar[]{previous, duration[p][k]}, completion[p][k]));
        } else if (previous == null) {
          m.cp().post(sum(new CPIntVar[]{before, duration[p][k]}, completion[p][k]));
        } else {
          m.cp().post(sum(new CPIntVar[]{max(new CPIntVar[]{before, previous}), duration[p][k]}, completion[p][k]));
        }
      }
    }

    // the makespan is the time the last job leaves the last machine
    CPIntVar makespan = m.intVar(0, horizon);
    m.cp().post(eq(makespan, completion[n - 1][machines - 1]));
    m.minimize(makespan);
    out.put("makespan", makespan);
  }
}
