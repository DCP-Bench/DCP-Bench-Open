// Graceful graphs (CSPLib 053): label the nodes of a graph with q edges by distinct
// values from 0..q so that the absolute differences across the edges are all different.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int q = inst.getInt("m");                  // number of edges
    int n = inst.getInt("n");                  // number of nodes
    int[][] graph = inst.getIntMatrix("graph"); // graph[e] = {x, y}: edge e joins nodes x and y

    // node labels are distinct values from 0..q
    IntVar[] nodes = m.intVarArray("node", n, 0, q, false);
    // every node gets a unique label
    m.allDifferent(nodes, "AC").post();

    // the label of edge xy is |f(x) - f(y)|; the edge labels are all different
    IntVar[] edges = new IntVar[q];
    for (int e = 0; e < q; e++) {
      int x = graph[e][0], y = graph[e][1];
      edges[e] = nodes[x].sub(nodes[y]).abs().intVar();
    }
    // the edge labels are pairwise different (and lie in 1..q, so they form a permutation)
    m.allDifferent(edges, "AC").post();

    out.put("nodes", nodes);
    out.put("edges", edges);
  }
}
