import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Bank card PIN abcd: four distinct digits where the 2-digit number cd is 3 times ab
// and the 2-digit number da is 2 times bc.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the PIN digits a, b, c, d
    IntVar a = m.intVar("a", 0, 9);
    IntVar b = m.intVar("b", 0, 9);
    IntVar c = m.intVar("c", 0, 9);
    IntVar d = m.intVar("d", 0, 9);

    // no two digits are the same
    m.allDifferent(new IntVar[]{a, b, c, d}, "AC").post();

    // the 2-digit numbers ab, bc, cd and da
    IntVar ab = m.intVar("ab", 0, 99);
    IntVar bc = m.intVar("bc", 0, 99);
    IntVar cd = m.intVar("cd", 0, 99);
    IntVar da = m.intVar("da", 0, 99);
    m.scalar(new IntVar[]{a, b, ab}, new int[]{10, 1, -1}, "=", 0).post();
    m.scalar(new IntVar[]{b, c, bc}, new int[]{10, 1, -1}, "=", 0).post();
    m.scalar(new IntVar[]{c, d, cd}, new int[]{10, 1, -1}, "=", 0).post();
    m.scalar(new IntVar[]{d, a, da}, new int[]{10, 1, -1}, "=", 0).post();

    // the 2-digit number cd is 3 times the 2-digit number ab
    m.scalar(new IntVar[]{cd, ab}, new int[]{1, -3}, "=", 0).post();

    // the 2-digit number da is 2 times the 2-digit number bc
    m.scalar(new IntVar[]{da, bc}, new int[]{1, -2}, "=", 0).post();

    out.put("a", a);
    out.put("b", b);
    out.put("c", c);
    out.put("d", d);
  }
}
