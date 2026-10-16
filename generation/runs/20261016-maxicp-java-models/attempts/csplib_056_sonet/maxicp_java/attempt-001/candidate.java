// SONET: nodes are placed on rings through add-drop multiplexers (ADMs). Every pair of nodes
// with a communication demand must share at least one ring, each ring holds at most its
// capacity of nodes, and the total number of ADMs is minimised.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");                       // number of nodes
    int r = inst.getInt("r");                       // number of rings
    int[][] demand = inst.getIntMatrix("demand");   // demand[i][j] > 0: nodes i and j communicate
    int[] capacity = inst.getIntArray("capacity_nodes"); // maximum number of nodes on ring k

    // ring_config[k][i] = 1 if node i is on ring k
    CPBoolVar[][] onRing = new CPBoolVar[r][];
    for (int k = 0; k < r; k++) onRing[k] = m.boolVarArray(n);

    // each ring can host at most its capacity of nodes
    for (int k = 0; k < r; k++) {
      m.cp().post(le(sum(onRing[k]), capacity[k]));
    }

    // for two nodes with a communication demand, they must be on at least one common ring
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        if (demand[i][j] == 0 && demand[j][i] == 0) continue;
        CPBoolVar[] together = new CPBoolVar[r];
        for (int k = 0; k < r; k++) {
          together[k] = isEq(sum(new CPIntVar[]{onRing[k][i], onRing[k][j]}), 2);
        }
        m.cp().post(or(together));
      }
    }

    // total number of ADMs: one per node installed on a ring
    CPIntVar[] all = new CPIntVar[r * n];
    for (int k = 0; k < r; k++)
      for (int i = 0; i < n; i++)
        all[k * n + i] = onRing[k][i];
    CPIntVar totalAdms = m.intVar(0, r * n);
    m.cp().post(eq(totalAdms, sum(all)));
    m.minimize(totalAdms);

    out.put("ring_config", onRing);
    out.put("total_adms", totalAdms);
  }
}
