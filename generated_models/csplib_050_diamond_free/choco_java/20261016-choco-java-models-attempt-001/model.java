// Diamond-free degree sequences: find a simple graph on N vertices with no induced
// diamond (no four vertices joined by five or more edges), whose degrees are all
// positive multiples of 3, sorted in non-increasing order, with degree sum a multiple of 12.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.List;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("N");

    // adjacency: x[i][j] = 1 if vertices i and j are joined by an edge
    BoolVar[][] x = new BoolVar[n][n];
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        // the graph is undirected: the pair {i, j} is one variable
        BoolVar e = m.boolVar("x_" + i + "_" + j);
        x[i][j] = e;
        x[j][i] = e;
      }
    }
    // simple graph: no loop edges
    BoolVar noLoop = m.boolVar("noLoop", false);
    for (int i = 0; i < n; i++) x[i][i] = noLoop;

    // each degree is positive and a multiple of 3, at most n - 1
    List<Integer> allowed = new ArrayList<>();
    for (int d = 3; d <= n - 1; d += 3) allowed.add(d);
    int[] dom = allowed.stream().mapToInt(Integer::intValue).toArray();
    IntVar[] deg = new IntVar[n];
    for (int i = 0; i < n; i++) {
      deg[i] = m.intVar("deg_" + i, dom);
      // the degree of vertex i is the number of its incident edges
      m.sum(x[i], "=", deg[i]).post();
    }

    // degree sequence is non-increasing
    for (int i = 0; i + 1 < n; i++) {
      m.arithm(deg[i], ">=", deg[i + 1]).post();
    }

    // the sum of the degrees is a multiple of 12 (|E| is a multiple of 6)
    IntVar total = m.intVar("total_degree", 0, n * (n - 1), true);
    m.sum(deg, "=", total).post();
    IntVar k = m.intVar("k", 0, n * (n - 1) / 12 + 1, true);
    total.eq(k.mul(12)).post();

    // diamond-free: every set of four vertices has at most four edges between them
    for (int a = 0; a < n; a++) {
      for (int b = a + 1; b < n; b++) {
        for (int c = b + 1; c < n; c++) {
          for (int d = c + 1; d < n; d++) {
            BoolVar[] pairs = {x[a][b], x[a][c], x[a][d], x[b][c], x[b][d], x[c][d]};
            // at most four of the six pairs are edges
            m.sum(pairs, "<=", 4).post();
          }
        }
      }
    }

    out.put("matrix", x);
  }
}
