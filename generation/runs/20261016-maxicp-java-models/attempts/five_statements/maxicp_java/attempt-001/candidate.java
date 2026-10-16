// Five statements: statement k (k = 1..5) says "exactly k of these statements are false".
// Decide for each statement whether it is true (1) or false (0), in the order of the statements.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // there are five statements, each either true or false
    CPBoolVar[] s = m.boolVarArray(5);
    // the number of true statements, the complement of the number of false ones
    CPIntVar trueCount = sum(s);
    for (int k = 1; k <= 5; k++) {
      // statement k is true exactly when exactly k of these statements are false,
      // that is, exactly 5 - k of them are true
      m.cp().post(eq(s[k - 1], isEq(trueCount, 5 - k)));
    }
    out.put("statements", s);
  }
}
