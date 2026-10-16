// Hardy's 1729 square: find four different numbers between 1 and 100 with a^2 + b^2 = c^2 + d^2.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the four numbers, each between 1 and 100
    IntVar a = m.intVar("a", 1, 100);
    IntVar b = m.intVar("b", 1, 100);
    IntVar c = m.intVar("c", 1, 100);
    IntVar d = m.intVar("d", 1, 100);

    // the four numbers are different
    m.allDifferent(new IntVar[]{a, b, c, d}, "AC").post();

    // squares of the four numbers, with bounds from 1..100
    IntVar aa = m.intVar("a2", 1, 10000, true);
    IntVar bb = m.intVar("b2", 1, 10000, true);
    IntVar cc = m.intVar("c2", 1, 10000, true);
    IntVar dd = m.intVar("d2", 1, 10000, true);
    m.square(aa, a).post();
    m.square(bb, b).post();
    m.square(cc, c).post();
    m.square(dd, d).post();

    // the sum of the squares of the first two numbers equals the sum of the squares of the other two
    m.scalar(new IntVar[]{aa, bb, cc, dd}, new int[]{1, 1, -1, -1}, "=", 0).post();

    out.put("a", a);
    out.put("b", b);
    out.put("c", c);
    out.put("d", d);
  }
}
