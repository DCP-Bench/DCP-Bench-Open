import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    CPIntVar x = m.intVar(0, 1);
    m.cp().post(eq(x, 0));
    m.cp().post(eq(x, 1));
    out.put("x", x);
  }
}
