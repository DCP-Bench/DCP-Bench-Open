import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

// Balanced incomplete block design: arrange v objects into b blocks so that each block
// holds exactly k objects, each object lies in exactly r blocks, and every two distinct
// objects lie together in exactly lambda blocks. The output is the v-by-b incidence matrix.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int v = inst.getInt("v");
    int b = inst.getInt("b");
    int r = inst.getInt("r");
    int k = inst.getInt("k");
    int lambda = inst.getInt("l");

    // matrix[i][j] = 1 if object i is in block j
    BoolVar[][] matrix = m.boolVarMatrix("matrix", v, b);

    // each object occurs in exactly r blocks
    for (int i = 0; i < v; i++) {
      m.sum(matrix[i], "=", r).post();
    }

    // each block contains exactly k objects
    for (int j = 0; j < b; j++) {
      BoolVar[] block = new BoolVar[v];
      for (int i = 0; i < v; i++) block[i] = matrix[i][j];
      m.sum(block, "=", k).post();
    }

    // every two distinct objects occur together in exactly lambda blocks:
    // the number of blocks holding both objects of a pair is the scalar product of their rows
    for (int p = 0; p < v; p++) {
      for (int q = p + 1; q < v; q++) {
        BoolVar[] both = new BoolVar[b];
        for (int j = 0; j < b; j++) {
          both[j] = m.boolVar("both_" + p + "_" + q + "_" + j);
          m.addClausesBoolAndArrayEqVar(new BoolVar[]{matrix[p][j], matrix[q][j]}, both[j]);
        }
        m.sum(both, "=", lambda).post();
      }
    }

    out.put("matrix", matrix);
  }
}
