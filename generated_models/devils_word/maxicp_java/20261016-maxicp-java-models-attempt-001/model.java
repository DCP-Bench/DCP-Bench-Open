// Devil's word: insert a '+' or '-' before each integer of the array so that the
// signed numbers sum to the total. Report the array with the signs applied.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] arr = inst.getIntArray("arr");
    int total = inst.getInt("total");
    int n = arr.length;

    CPIntVar[] result = new CPIntVar[n];
    // each number gets a '+' or a '-' in front of it
    for (int i = 0; i < n; i++) {
      int a = arr[i];
      result[i] = m.intVar(Math.min(a, -a), Math.max(a, -a));
      m.cp().post(or(new CPBoolVar[] { isEq(result[i], a), isEq(result[i], -a) }));
    }

    // summing the signed numbers gives the total 666
    m.cp().post(eq(sum(result), total));

    out.put("result", result);
  }
}
