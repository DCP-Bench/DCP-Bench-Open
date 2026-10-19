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
    CPIntVar[] v = m.intVarArray(4, 0, 2);
    CPIntVar total = sum(v);
    m.cp().post(ge(total, n));
    m.minimize(total);
    out.put("x", v);
  }
}
