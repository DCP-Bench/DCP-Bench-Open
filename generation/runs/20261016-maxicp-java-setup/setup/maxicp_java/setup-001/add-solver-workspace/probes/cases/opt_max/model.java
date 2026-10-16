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
    CPIntVar x = m.intVar(0, 2 * n);
    CPIntVar y = m.intVar(0, 2 * n);
    m.cp().post(le(sum(x, y), 2 * n));
    m.maximize(sum(x, y));
    out.put("x", x);
    out.put("y", y);
  }
}
