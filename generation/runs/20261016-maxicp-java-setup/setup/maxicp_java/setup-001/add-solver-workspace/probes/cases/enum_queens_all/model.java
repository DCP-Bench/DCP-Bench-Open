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
    CPIntVar[] q = m.intVarArray(n, 0, n - 1);
    CPIntVar[] qL = CPFactory.makeIntVarArray(n, i -> minus(q[i], i));
    CPIntVar[] qR = CPFactory.makeIntVarArray(n, i -> plus(q[i], i));
    m.cp().post(allDifferent(q));
    m.cp().post(allDifferent(qL));
    m.cp().post(allDifferent(qR));
    out.put("q", q);
  }
}
