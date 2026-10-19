import java.util.Arrays;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// 13 people enter a room one at a time, 4 of them male and 9 female.
// sequence[i] is 0 for a male and 1 for a female entering at position i.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = 13;
    int males = 4;

    CPBoolVar[] sequence = m.boolVarArray(n);

    // 4 of the 13 people are male, so 9 are female
    m.cp().post(sum(sequence, n - males));

    // at any one time the ratio of females to males in the room is no greater than 7/3:
    // with f females and m males, f / m <= 7 / 3, which with m = t - f gives 10 f <= 7 t.
    // The bound is f <= floor(7 t / 10), so the first person to enter must be male.
    for (int t = 1; t <= n; t++) {
      CPBoolVar[] inRoom = Arrays.copyOfRange(sequence, 0, t);
      CPIntVar females = m.intVar(0, t);
      m.cp().post(eq(females, sum(inRoom)));
      m.cp().post(le(females, (7 * t) / 10));
    }

    out.put("sequence", sequence);
  }
}
