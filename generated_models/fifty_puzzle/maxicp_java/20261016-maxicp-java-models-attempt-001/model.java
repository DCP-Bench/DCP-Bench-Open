import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Fifty puzzle (Loyd's dummies): a number of dummies carry numbers. Choose
// which dummies to knock over so that the sum of their numbers is exactly
// the target sum. Output dummies[i] is true when dummy i is knocked over.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the numbers on the dummies, one per dummy
    int[] values = inst.getIntArray("values");
    // the target sum the knocked-over numbers must add up to exactly
    int target = inst.getInt("target_sum");
    int n = values.length;

    // dummies[i] = 1 if dummy i is knocked over
    CPBoolVar[] dummies = m.boolVarArray(n);

    // the numbers on all the men that you knock down
    CPIntVar[] terms = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      terms[i] = mul(dummies[i], values[i]);
    }

    // when the sum amounts to exactly a given target sum, neither more nor less
    m.cp().post(eq(sum(terms), target));

    out.put("dummies", dummies);
  }
}
