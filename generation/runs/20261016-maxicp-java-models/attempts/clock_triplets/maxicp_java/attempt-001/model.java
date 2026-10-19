import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Clock triplets: arrange the numbers 1 to 12 on the face of a clock so that
// no triplet of adjacent numbers has a sum higher than 21.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // x[i] = the number at clock position i (positions 0..11, clockwise)
    CPIntVar[] x = m.intVarArray(12, 1, 12);

    // the numbers on the clock are all different, and together they are 1 to 12
    m.cp().post(allDifferent(x));

    // every triplet of adjacent numbers on the clock (wrapping around 12 to 1)
    // has a sum of at most 21
    for (int i = 0; i < 12; i++) {
      m.cp().post(le(sum(new CPIntVar[] { x[i], x[(i + 1) % 12], x[(i + 2) % 12] }), 21));
    }

    out.put("x", x);
  }
}
