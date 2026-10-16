import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    CPIntVar x = m.intVar(0, n);
    CPIntVar y = m.intVar(0, n);
    if (inst.getBool("optimize")) {
      m.cp().post(ge(sum(x, y), n));
      m.minimize(sum(x, y));
    } else {
      m.cp().post(eq(sum(x, y), n));
    }
    out.put("x", x);
    out.put("y", y);
  }
}
