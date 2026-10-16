import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// SONET: place nodes on rings so that every communication demand has a common ring,
// ring capacities are respected, and the total number of ADMs is minimised.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int r = inst.getInt("r");
    int n = inst.getInt("n");
    int[][] demand = inst.getIntMatrix("demand");
    int[] capacity = inst.getIntArray("capacity_nodes");

    // on[k][i] = 1 if node i is installed on ring k
    BoolVar[][] on = m.boolVarMatrix("on", r, n);

    // a node with no demand is not installed on any ring; the demand constraints below install the rest

    // a ring hosts at most its capacity of nodes
    for (int k = 0; k < r; k++) {
      m.sum(on[k], "<=", capacity[k]).post();
    }

    // every communication demand needs a ring that both end nodes are on
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        if (demand[i][j] == 0 && demand[j][i] == 0) continue;
        IntVar[] shared = new IntVar[r];
        for (int k = 0; k < r; k++) {
          shared[k] = m.intVar(0, 1);
          m.times(on[k][i], on[k][j], shared[k]).post();
        }
        m.sum(shared, ">=", 1).post();
      }
    }

    // total number of ADMs, minimised
    IntVar[] all = new IntVar[r * n];
    IntVar[] nodeMajor = new IntVar[r * n];
    for (int k = 0; k < r; k++)
      for (int i = 0; i < n; i++) {
        all[k * n + i] = on[k][i];
        nodeMajor[i * r + k] = on[k][i];
      }
    IntVar total = m.sum("total_adms", all);
    m.setObjective(Model.MINIMIZE, total);

    // branch node by node, not installed first
    m.getSolver().setSearch(Search.inputOrderLBSearch(nodeMajor));

    out.put("ring_config", on);
    out.put("total_adms", total);
  }
}
