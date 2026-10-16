import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Quasigroup existence QG3.m: an order m Latin square Q, with a*b = Q[a][b],
// such that (a*b)*(b*a) = a for every a and b. Values and indices are 0..m-1.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("m");

    // the cell Q[i][j] has the value k exactly when x[i][j][k] is 1
    CPBoolVar[][][] x = new CPBoolVar[n][n][n];
    CPIntVar[][] q = new CPIntVar[n][n];
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        CPIntVar[] terms = new CPIntVar[n];
        for (int k = 0; k < n; k++) {
          x[i][j][k] = m.boolVar();
          terms[k] = mul(x[i][j][k], k);
        }
        // each cell holds exactly one value
        m.cp().post(eq(sum(x[i][j]), 1));
        q[i][j] = m.intVar(0, n - 1);
        m.cp().post(eq(sum(terms), q[i][j]));
      }
    }

    // each element occurs once in every row
    for (int i = 0; i < n; i++) {
      for (int k = 0; k < n; k++) {
        CPIntVar[] row = new CPIntVar[n];
        for (int j = 0; j < n; j++) row[j] = x[i][j][k];
        m.cp().post(eq(sum(row), 1));
      }
    }

    // each element occurs once in every column
    for (int j = 0; j < n; j++) {
      for (int k = 0; k < n; k++) {
        CPIntVar[] col = new CPIntVar[n];
        for (int i = 0; i < n; i++) col[i] = x[i][j][k];
        m.cp().post(eq(sum(col), 1));
      }
    }

    // (a*b)*(b*a) = a for every a and b
    for (int a = 0; a < n; a++) {
      for (int b = 0; b < n; b++) {
        // if a*b is c and b*a is d, then (a*b)*(b*a) = c*d is a
        for (int c = 0; c < n; c++) {
          for (int d = 0; d < n; d++) {
            m.cp().post(or(new CPBoolVar[] {
              not(x[a][b][c]), not(x[b][a][d]), x[c][d][a]
            }));
          }
        }
      }
    }

    out.put("quasigroup", q);
  }
}
