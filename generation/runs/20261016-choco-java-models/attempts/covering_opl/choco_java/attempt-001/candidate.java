import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Covering: select a set of workers so that every task is performed by at least one hired
// worker, minimising the total hiring cost.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int nWorkers = inst.getInt("nb_workers");
    int nTasks = inst.getInt("num_tasks");
    int[] cost = inst.getIntArray("Cost");
    int[][] qualified = inst.getIntMatrix("Qualified"); // qualified[t]: 1-based ids of workers able to do task t

    // workers[w]: 1 if worker w is hired
    BoolVar[] workers = m.boolVarArray("workers", nWorkers);

    // every task is performed by at least one hired worker who is qualified for it
    for (int t = 0; t < nTasks; t++) {
      BoolVar[] able = new BoolVar[qualified[t].length];
      for (int k = 0; k < qualified[t].length; k++) {
        able[k] = workers[qualified[t][k] - 1];
      }
      m.sum(able, ">=", 1).post();
    }

    // total hiring cost of the selected workers
    int maxCost = 0;
    for (int c : cost) maxCost += c;
    IntVar total = m.intVar("total_cost", 0, maxCost, true);
    m.scalar(workers, cost, "=", total).post();
    m.setObjective(Model.MINIMIZE, total);

    out.put("total_cost", total);
    out.put("workers", workers);
  }
}
