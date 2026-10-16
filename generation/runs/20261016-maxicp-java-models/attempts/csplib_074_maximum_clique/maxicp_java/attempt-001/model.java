import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Maximum clique: find a largest set of vertices of a simple undirected graph
// in which every two distinct vertices are adjacent. c[i] = 1 if vertex i is in the clique.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int[][] adj = inst.getIntMatrix("adj");

    // c[i] = 1 if vertex i is in the clique
    CPBoolVar[] c = m.boolVarArray(n);

    // every two distinct vertices in the clique are adjacent:
    // two vertices with no edge between them cannot both be in the clique
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        if (adj[i][j] == 0) {
          m.cp().post(le(sum(c[i], c[j]), 1));
        }
      }
    }

    // the clique size is the number of chosen vertices, and it is maximised
    CPIntVar size = m.intVar(0, n);
    m.cp().post(eq(size, sum(c)));
    m.maximize(size);

    out.put("c", c);
  }
}
