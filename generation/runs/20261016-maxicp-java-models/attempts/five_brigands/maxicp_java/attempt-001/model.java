import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Five Spanish brigands (Alfonso A, Benito B, Carlos C, Diego D, Esteban E)
// divide exactly 200 doubloons, and each has at least one doubloon.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // every brigand has at least one doubloon
    CPIntVar a = m.intVar(1, 200);
    CPIntVar b = m.intVar(1, 200);
    CPIntVar c = m.intVar(1, 200);
    CPIntVar d = m.intVar(1, 200);
    CPIntVar e = m.intVar(1, 200);

    // they captured altogether exactly 200 doubloons
    m.cp().post(eq(sum(a, b, c, d, e), 200));

    // if Alfonso had twelve times as much, Benito three times as much, Carlos the same
    // amount, Diego half as much and Esteban one-third as much, the total is still 200.
    // Multiplied by 6 to keep integer coefficients:
    // 6*(12a + 3b + c + d/2 + e/3) = 72a + 18b + 6c + 3d + 2e = 1200
    m.cp().post(eq(sum(mul(a, 72), mul(b, 18), mul(c, 6), mul(d, 3), mul(e, 2)), 1200));

    out.put("A", a);
    out.put("B", b);
    out.put("C", c);
    out.put("D", d);
    out.put("E", e);
  }
}
