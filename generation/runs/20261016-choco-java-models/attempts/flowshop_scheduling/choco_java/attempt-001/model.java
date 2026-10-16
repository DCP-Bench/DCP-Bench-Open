import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Permutation flow shop: every job goes through machines 1 to M in that order, and all jobs
// use the machines in the same sequence. Find the job sequence that minimises the time when
// all jobs have been processed (the makespan).
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] pt = inst.getIntMatrix("process_time");  // pt[j][k]: time of job j on machine k
    int n = pt.length;                               // number of jobs
    int machines = pt[0].length;                     // number of machines

    int horizon = 0;                                 // all jobs back to back is an upper bound
    for (int[] row : pt) for (int t : row) horizon += t;

    // seq[p]: the job (0-based) at position p of the sequence, every job exactly once
    IntVar[] seq = m.intVarArray("seq", n, 0, n - 1);
    m.allDifferent(seq, "AC").post();

    IntVar[][] dur = new IntVar[n][machines];        // dur[p][k]: time of the job at position p on machine k
    IntVar[][] start = new IntVar[n][machines];      // start[p][k]: start of the job at position p on machine k
    for (int k = 0; k < machines; k++) {
      int[] column = new int[n];
      int lo = Integer.MAX_VALUE, hi = 0;
      for (int j = 0; j < n; j++) {
        column[j] = pt[j][k];
        lo = Math.min(lo, column[j]);
        hi = Math.max(hi, column[j]);
      }
      for (int p = 0; p < n; p++) {
        dur[p][k] = m.intVar("dur" + p + "_" + k, lo, hi, true);
        // the processing time of the job at position p on machine k
        m.element(dur[p][k], column, seq[p]).post();
        start[p][k] = m.intVar("start" + p + "_" + k, 0, horizon, true);
      }
    }

    // a job goes through the machines in order: it leaves machine k before it starts on machine k+1
    for (int p = 0; p < n; p++)
      for (int k = 0; k + 1 < machines; k++)
        start[p][k].add(dur[p][k]).le(start[p][k + 1]).post();

    // a machine works on one job at a time, in sequence order: the job at position p
    // leaves machine k before the job at position p+1 starts on machine k
    for (int p = 0; p + 1 < n; p++)
      for (int k = 0; k < machines; k++)
        start[p][k].add(dur[p][k]).le(start[p + 1][k]).post();

    // the makespan is when the last job leaves the last machine
    IntVar makespan = m.intVar("makespan", 0, horizon, true);
    start[n - 1][machines - 1].add(dur[n - 1][machines - 1]).eq(makespan).post();
    m.setObjective(Model.MINIMIZE, makespan);

    // choose the sequence first, then start each job as early as possible
    IntVar[] starts = new IntVar[n * machines];
    for (int p = 0; p < n; p++)
      for (int k = 0; k < machines; k++) starts[p * machines + k] = start[p][k];
    m.getSolver().setSearch(Search.inputOrderLBSearch(seq), Search.inputOrderLBSearch(starts));

    out.put("makespan", makespan);
  }
}
