import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Maximal independent set: choose nodes so that no two chosen nodes are adjacent,
// and every node left out is adjacent to a chosen node.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int[][] adjacency = inst.getIntMatrix("adjacency_list");  // 1-based neighbours of each node
    BoolVar[] in = m.boolVarArray("in", n);                   // in[i]: node i is in the set

    // no two of the chosen nodes are adjacent: for each node and each neighbour,
    // at most one of the two is in the set
    for (int i = 0; i < n; i++) {
      for (int nb : adjacency[i]) {
        m.sum(new IntVar[]{in[i], in[nb - 1]}, "<=", 1).post();
      }
    }

    // maximal: each node is in the set or has a neighbour in the set
    for (int i = 0; i < n; i++) {
      IntVar[] closed = new IntVar[adjacency[i].length + 1];
      closed[0] = in[i];
      for (int k = 0; k < adjacency[i].length; k++) closed[k + 1] = in[adjacency[i][k] - 1];
      m.sum(closed, ">=", 1).post();
    }

    out.put("nodes", in);
  }
}
