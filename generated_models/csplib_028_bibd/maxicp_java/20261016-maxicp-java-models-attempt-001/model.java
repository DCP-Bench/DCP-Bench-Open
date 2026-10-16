import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Balanced incomplete block design: a v by b binary incidence matrix.
// Each row has exactly r ones, each column exactly k ones, and every
// pair of distinct rows has a scalar product of lambda.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int v = inst.getInt("v");
    int b = inst.getInt("b");
    int r = inst.getInt("r");
    int k = inst.getInt("k");
    int lambda = inst.getInt("l");

    // a v by b matrix of 0/1 decisions
    CPBoolVar[][] x = new CPBoolVar[v][];
    for (int i = 0; i < v; i++) {
      x[i] = m.boolVarArray(b);
    }

    // each object occurs in exactly r different blocks
    for (int i = 0; i < v; i++) {
      m.cp().post(eq(sum(x[i]), r));
    }

    // each block contains exactly k distinct objects
    for (int c = 0; c < b; c++) {
      CPIntVar[] col = new CPIntVar[v];
      for (int i = 0; i < v; i++) {
        col[i] = x[i][c];
      }
      m.cp().post(eq(sum(col), k));
    }

    // every two distinct objects occur together in exactly lambda blocks:
    // the scalar product of two distinct rows is lambda, where the
    // product of two 0/1 values is their minimum
    for (int i = 0; i < v; i++) {
      for (int j = i + 1; j < v; j++) {
        CPIntVar[] both = new CPIntVar[b];
        for (int c = 0; c < b; c++) {
          both[c] = minimum(new CPIntVar[] {x[i][c], x[j][c]});
        }
        m.cp().post(eq(sum(both), lambda));
      }
    }

    out.put("matrix", x);
  }
}
