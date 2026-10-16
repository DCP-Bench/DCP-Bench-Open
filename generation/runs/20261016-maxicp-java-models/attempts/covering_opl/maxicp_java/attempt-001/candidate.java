// Covering: select a set of workers to perform all the tasks while minimizing the total hiring
// cost. Each worker has a hiring cost Cost[w]. Each task t can be performed by the workers
// listed in Qualified[t] (1-based worker numbers). Every task must be performed by at least
// one hired worker.
// Outputs: workers[w] is true when worker w is hired; total_cost is the sum of the hiring
// costs of the hired workers.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int nbWorkers = inst.getInt("nb_workers");
    int[] cost = inst.getIntArray("Cost");
    int[][] qualified = inst.getIntMatrix("Qualified");

    // workers[w] = 1 if worker w is hired
    CPBoolVar[] workers = m.boolVarArray(nbWorkers);

    // every task is performed by at least one hired worker qualified for it
    for (int t = 0; t < qualified.length; t++) {
      CPIntVar[] candidates = new CPIntVar[qualified[t].length];
      for (int k = 0; k < qualified[t].length; k++) {
        candidates[k] = workers[qualified[t][k] - 1];
      }
      if (candidates.length == 0) {
        // no worker can perform this task: the covering is impossible
        CPIntVar none = m.intVar(0, 0);
        m.cp().post(ge(none, 1));
      } else {
        m.cp().post(ge(sum(candidates), 1));
      }
    }

    // total hiring cost of the hired workers
    int maxCost = 0;
    for (int c : cost) maxCost += c;
    CPIntVar totalCost = m.intVar(0, maxCost);
    CPIntVar[] payments = new CPIntVar[nbWorkers];
    for (int w = 0; w < nbWorkers; w++) payments[w] = mul(workers[w], cost[w]);
    m.cp().post(eq(sum(payments), totalCost));

    // minimize the total hiring cost
    m.minimize(totalCost);

    out.put("total_cost", totalCost);
    out.put("workers", workers);
  }
}
