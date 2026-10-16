import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Broken weight: a weight of M pounds broke into n pieces of whole-pound weights. The pieces
// must weigh every whole number from 1 to M on a balance scale, where a piece can go on the
// object's side, on the other side, or off the scale. Find the weights of the pieces.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int M = inst.getInt("m");  // total weight of the broken piece, in pounds
    int n = inst.getInt("n");  // number of pieces

    // weights[i]: weight of piece i, a whole number of pounds
    IntVar[] weights = m.intVarArray("weights", n, 1, M);

    // the pieces together make up the whole weight
    m.sum(weights, "=", M).post();

    // the pieces have different weights, listed lightest first (fixes the order of equal sets of pieces)
    m.allDifferent(weights, "AC").post();
    m.increasing(weights, 1).post();

    // every whole weight t from 1 to M can be weighed: each piece is on the object's side (-1),
    // off the scale (0), or on the other side (+1), so the signed weights of the pieces sum to t
    for (int t = 1; t <= M; t++) {
      IntVar[] signed = new IntVar[n];
      for (int i = 0; i < n; i++) {
        IntVar side = m.intVar("side_" + t + "_" + i, -1, 1);
        signed[i] = m.intVar("signed_" + t + "_" + i, -M, M);
        m.times(side, weights[i], signed[i]).post();
      }
      m.sum(signed, "=", t).post();
    }

    m.getSolver().setSearch(Search.inputOrderLBSearch(weights));
    out.put("weights", weights);
  }
}
