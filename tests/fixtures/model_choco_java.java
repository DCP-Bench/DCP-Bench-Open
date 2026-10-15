import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    IntVar x = m.intVar("x", 0, n);
    IntVar y = m.intVar("y", 0, n);
    if (inst.getBool("optimize")) {
      m.arithm(x, "+", y, ">=", n).post();
      IntVar total = m.intVar("total", 0, 2 * n);
      m.sum(new IntVar[]{x, y}, "=", total).post();
      m.setObjective(Model.MINIMIZE, total);
    } else {
      m.arithm(x, "+", y, "=", n).post();
    }
    out.put("x", x);
    out.put("y", y);
  }
}
