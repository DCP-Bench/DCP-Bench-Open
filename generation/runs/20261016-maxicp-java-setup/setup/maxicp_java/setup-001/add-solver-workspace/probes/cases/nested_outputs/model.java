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
    CPIntVar x = m.intVar(0, n);
    CPIntVar y = m.intVar(0, n);
    m.cp().post(eq(sum(x, y), n));
    out.put("cube", new CPIntVar[][][]{{{x, y}, {y, x}}});
    out.put("flags", java.util.List.of(new CPIntVar[]{x, y}));
    CPIntVar[] digits = new CPIntVar[11];
    digits[0] = CPFactory.makeIntVar(m.cp(), 3, 3);
    for (int i = 1; i < 9; i++) digits[i] = CPFactory.makeIntVar(m.cp(), 0, 0);
    digits[9] = x;
    digits[10] = y;
    out.putDigits("big", digits, 10);
    out.put("k", 5);
  }
}
