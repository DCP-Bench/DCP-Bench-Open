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
    CPIntVar x = m.intVar(0, 10);
    m.cp().post(ge(x, n));
    CPIntVar[] marks = m.intVarArray(11, 0, 200);
    m.cp().post(eq(marks[0], 0));
    for (int i = 0; i < 10; i++) m.cp().post(lt(marks[i], marks[i + 1]));
    CPIntVar[] diffs = new CPIntVar[55];
    int k = 0;
    for (int i = 0; i < 11; i++) for (int j = i + 1; j < 11; j++) {
      CPIntVar d = m.intVar(0, 200);
      m.cp().post(sum(new CPIntVar[]{marks[j], minus(marks[i])}, d));
      diffs[k++] = d;
    }
    m.cp().post(allDifferent(diffs));
    m.minimize(sum(mul(x, 1000), marks[10]));
    out.put("x", x);
  }
}
