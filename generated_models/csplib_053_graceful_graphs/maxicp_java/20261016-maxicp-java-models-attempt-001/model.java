// Graceful graphs: label the nodes of a graph with q edges by distinct labels
// from {0..q} so that the edge labels |f(x) - f(y)| are all different.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");          // number of nodes
    int q = inst.getInt("m");          // number of edges
    int[][] graph = inst.getIntMatrix("graph");   // edge k joins nodes graph[k][0] and graph[k][1], 0-based

    // a labelling f of the nodes: each node gets a unique label from {0, ..., q}
    CPIntVar[] nodes = m.intVarArray(n, 0, q);
    // the labels of the nodes are all different
    m.cp().post(allDifferent(nodes));

    // the edge labels: edge xy is labelled with |f(x) - f(y)|, a value in 1..q
    CPIntVar[] edges = m.intVarArray(q, 1, q);

    // the allowed triples (f(x), f(y), |f(x) - f(y)|) for two different node labels
    int numRows = (q + 1) * q;
    int[][] absDiff = new int[numRows][];
    int r = 0;
    for (int a = 0; a <= q; a++) {
      for (int b = 0; b <= q; b++) {
        if (a == b) continue;
        absDiff[r++] = new int[] { a, b, Math.abs(a - b) };
      }
    }
    for (int k = 0; k < q; k++) {
      CPIntVar x = nodes[graph[k][0]];
      CPIntVar y = nodes[graph[k][1]];
      // edge k is labelled with the absolute difference of its two end labels
      m.cp().post(table(new CPIntVar[] { x, y, edges[k] }, absDiff));
    }
    // the edge labels are all different
    m.cp().post(allDifferent(edges));

    out.put("nodes", nodes);
    out.put("edges", edges);
  }
}
