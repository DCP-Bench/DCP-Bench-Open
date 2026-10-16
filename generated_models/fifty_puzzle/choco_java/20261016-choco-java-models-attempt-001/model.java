import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

// Fifty puzzle: choose which dummies to knock over so that the numbers on the knocked
// dummies add up to exactly the target sum.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] values = inst.getIntArray("values");   // number on each dummy
    int target = inst.getInt("target_sum");      // the exact sum to hit

    // dummies[i] = 1 if dummy i is knocked over
    BoolVar[] dummies = m.boolVarArray("dummies", values.length);

    // the numbers on the knocked-over dummies add up to exactly the target sum
    m.scalar(dummies, values, "=", target).post();

    out.put("dummies", dummies);
  }
}
