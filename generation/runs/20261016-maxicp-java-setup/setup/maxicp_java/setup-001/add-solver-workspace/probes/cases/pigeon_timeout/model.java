import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    CPIntVar[] p = m.intVarArray(20, 0, 18);
    for (int i = 0; i < 20; i++) for (int j = i + 1; j < 20; j++) m.cp().post(neq(p[i], p[j]));
    out.put("p", p);
  }
}
