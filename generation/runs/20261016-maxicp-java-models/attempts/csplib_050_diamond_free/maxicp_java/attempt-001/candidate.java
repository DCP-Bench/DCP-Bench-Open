// Diamond-free degree sequences: find a simple graph on n vertices with no
// diamond (no 4 vertices spanning 5 or more edges), where every degree is
// positive and divisible by 3, the degrees are sorted non-increasing, and the
// sum of the degrees is divisible by 12. Output: the adjacency matrix.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // n = number of vertices, from the instance
    int n = inst.getInt("N");

    // edge[i][j] = 1 if vertices i and j are adjacent (symmetric, no loops)
    CPBoolVar[][] edge = new CPBoolVar[n][n];
    for (int i = 0; i < n; i++) {
      for (int j = i; j < n; j++) {
        if (i == j) {
          // no loop edges: the graph is simple
          CPBoolVar loop = m.boolVar();
          m.cp().post(eq(loop, 0));
          edge[i][i] = loop;
        } else {
          // the edge {i, j} is in E if and only if i is adjacent to j (undirected)
          CPBoolVar e = m.boolVar();
          edge[i][j] = e;
          edge[j][i] = e;
        }
      }
    }

    // each degree d_i is the number of edges incident on vertex i
    CPIntVar[] deg = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      deg[i] = sum(edge[i]);
    }

    // each degree is greater than zero and modulo 3 (divisible by 3):
    // d_i = 3 * q_i with 1 <= q_i <= (n - 1) / 3, since a degree is at most n - 1
    CPIntVar[] q = m.intVarArray(n, 1, (n - 1) / 3);
    for (int i = 0; i < n; i++) {
      m.cp().post(eq(deg[i], mul(q[i], 3)));
    }

    // the degree sequence is d_1 >= d_2 >= ... >= d_n
    for (int i = 0; i + 1 < n; i++) {
      m.cp().post(ge(deg[i], deg[i + 1]));
    }

    // the sum of the degrees is modulo 12: sum of degrees = 12 * t
    CPIntVar t = m.intVar(0, n * (n - 1) / 12);
    m.cp().post(eq(sum(deg), mul(t, 12)));

    // diamond-free: for every set of four vertices, the number of edges between
    // those four vertices is at most four (no diamond as an induced subgraph)
    for (int a = 0; a < n; a++) {
      for (int b = a + 1; b < n; b++) {
        for (int c = b + 1; c < n; c++) {
          for (int d = c + 1; d < n; d++) {
            CPBoolVar[] six = {
              edge[a][b], edge[a][c], edge[a][d],
              edge[b][c], edge[b][d], edge[c][d]
            };
            m.cp().post(le(sum(six), 4));
          }
        }
      }
    }

    // print the adjacency matrix of the graph
    out.put("matrix", edge);
  }
}
