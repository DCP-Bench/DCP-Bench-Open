// Maximal independent set: find a set of graph nodes that has no two adjacent nodes
// and that is not a subset of any other independent set. Output nodes[i] = 1 if node i is in the set.
import org.maxicp.cp.engine.core.CPBoolVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    // adjacency_list[i] holds the neighbours of node i+1 in 1-based node numbers
    int[][] adj = inst.getIntMatrix("adjacency_list");

    CPBoolVar[] nodes = m.boolVarArray(n);

    // no two adjacent nodes are both in the set (the set is independent)
    for (int i = 0; i < n; i++) {
      for (int k : adj[i]) {
        int j = k - 1;
        m.cp().post(or(new CPBoolVar[]{not(nodes[i]), not(nodes[j])}));
      }
    }

    // every node not in the set is adjacent to a node in the set (the set cannot be extended)
    for (int i = 0; i < n; i++) {
      CPBoolVar[] cover = new CPBoolVar[adj[i].length + 1];
      cover[0] = nodes[i];
      for (int k = 0; k < adj[i].length; k++) {
        cover[k + 1] = nodes[adj[i][k] - 1];
      }
      m.cp().post(or(cover));
    }

    out.put("nodes", nodes);
  }
}
