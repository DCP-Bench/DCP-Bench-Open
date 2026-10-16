import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Pythagorean triplet: find three natural numbers a < b < c with a^2 + b^2 = c^2
// and a + b + c = 1000.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int total = 1000;

    // a, b, c are natural numbers; each is below the total
    IntVar a = m.intVar("a", 1, total - 2, true);
    IntVar b = m.intVar("b", 1, total - 2, true);
    IntVar c = m.intVar("c", 1, total - 2, true);

    // a < b < c
    m.arithm(a, "<", b).post();
    m.arithm(b, "<", c).post();

    // a^2 + b^2 = c^2
    IntVar aa = m.intVar("aa", 1, total * total, true);
    IntVar bb = m.intVar("bb", 1, total * total, true);
    IntVar cc = m.intVar("cc", 1, total * total, true);
    m.square(aa, a).post();
    m.square(bb, b).post();
    m.square(cc, c).post();
    m.sum(new IntVar[]{aa, bb}, "=", cc).post();

    // a + b + c = 1000
    m.sum(new IntVar[]{a, b, c}, "=", total).post();

    out.put("a", a);
    out.put("b", b);
    out.put("c", c);
  }
}
