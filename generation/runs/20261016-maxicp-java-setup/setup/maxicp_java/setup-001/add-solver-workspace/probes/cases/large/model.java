import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    CPIntVar[] b = m.intVarArray(3000, 0, 1);
    CPIntVar count = m.intVar(0, 3000);
    m.cp().post(eq(count, sum(b)));
    m.cp().post(eq(count, n));
    out.put("b", b);
    out.put("count", count);
  }
}
