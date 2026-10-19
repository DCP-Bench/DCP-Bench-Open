import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Bank card PIN abcd: four digits a, b, c, d, print the PIN (a, b, c, d).
// Each of the two-digit numbers ab, cd, bc, da has a non-zero leading digit,
// so every digit is in 1..9.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    CPIntVar a = m.intVar(1, 9);
    CPIntVar b = m.intVar(1, 9);
    CPIntVar c = m.intVar(1, 9);
    CPIntVar d = m.intVar(1, 9);

    // no two digits are the same
    m.cp().post(allDifferent(new CPIntVar[] {a, b, c, d}));

    // the 2-digit number cd is 3 times the 2-digit number ab
    m.cp().post(eq(sum(mul(c, 10), d), sum(mul(a, 30), mul(b, 3))));

    // the 2-digit number da is 2 times the 2-digit number bc
    m.cp().post(eq(sum(mul(d, 10), a), sum(mul(b, 20), mul(c, 2))));

    out.put("a", a);
    out.put("b", b);
    out.put("c", c);
    out.put("d", d);
  }
}
