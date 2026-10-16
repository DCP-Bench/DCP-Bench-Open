import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Bus driver scheduling: choose a set of shifts so that every piece of work
// is covered by exactly one chosen shift, minimising the number of shifts chosen.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int numWork = inst.getInt("num_work");
    int numShifts = inst.getInt("num_shifts");

    // one Boolean per shift: 1 when the shift is selected
    CPBoolVar[] x = m.boolVarArray(numShifts);

    // each shift covers a list of pieces of work (task indices are 0-based)
    int[][] shifts = inst.getIntMatrix("shifts");

    // every piece of work is covered by exactly one selected shift
    for (int w = 0; w < numWork; w++) {
      java.util.List<CPIntVar> covering = new java.util.ArrayList<>();
      for (int s = 0; s < numShifts; s++) {
        for (int t : shifts[s]) {
          if (t == w) {
            covering.add(x[s]);
            break;
          }
        }
      }
      m.cp().post(eq(sum(covering.toArray(new CPIntVar[0])), 1));
    }

    // the number of selected shifts is minimised
    m.minimize(sum(x));

    out.put("x", x);
  }
}
