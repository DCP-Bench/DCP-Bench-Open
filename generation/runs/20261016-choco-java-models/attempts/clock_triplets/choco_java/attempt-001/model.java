import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Clock triplets: place the numbers 1 to 12 around a clock face so that no three adjacent
// numbers sum to more than 21.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // x[p] = number at clock position p (positions 0..11 in order around the face)
    IntVar[] x = m.intVarArray("x", 12, 1, 12);
    m.allDifferent(x, "AC").post();

    // no triplet of adjacent numbers (wrapping around the clock) sums to more than 21
    for (int p = 0; p < 12; p++) {
      IntVar[] triplet = {x[p], x[(p + 1) % 12], x[(p + 2) % 12]};
      m.sum(triplet, "<=", 21).post();
    }

    out.put("x", x);
  }
}
