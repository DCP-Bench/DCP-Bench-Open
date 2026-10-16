// Maximum clique: choose a set of vertices of a simple undirected graph such that every
// two chosen vertices are adjacent, and the set is as large as possible.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int[][] adj = inst.getIntMatrix("adj");   // adj[i][j] = 1 if vertices i and j are adjacent

    // x[i] = 1 if vertex i is in the clique
    BoolVar[] x = m.boolVarArray("x", n);

    // every two distinct vertices of the clique are adjacent:
    // two non-adjacent vertices cannot both be chosen
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        if (adj[i][j] == 0) {
          m.arithm(x[i], "+", x[j], "<=", 1).post();
        }
      }
    }

    // the clique size is the number of chosen vertices, to be maximised
    IntVar size = m.sum("size", x);
    m.setObjective(Model.MAXIMIZE, size);

    out.put("c", x);
  }
}
