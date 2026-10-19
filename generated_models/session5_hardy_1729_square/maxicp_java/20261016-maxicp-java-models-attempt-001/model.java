// Hardy's 1729 square: find four different numbers a, b, c, d between 1 and 100
// such that a^2 + b^2 = c^2 + d^2.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // numbers between 1 and 100
    CPIntVar a = m.intVar(1, 100);
    CPIntVar b = m.intVar(1, 100);
    CPIntVar c = m.intVar(1, 100);
    CPIntVar d = m.intVar(1, 100);

    // 4 different numbers
    m.cp().post(allDifferent(new CPIntVar[] {a, b, c, d}));

    // squares of the numbers, indexed by the number itself (0..100)
    int[] sq = new int[101];
    for (int i = 0; i <= 100; i++) sq[i] = i * i;

    // the sum of the squares of the two first numbers is equal to
    // the sum of the squares of the other two numbers
    CPIntVar sa = element(sq, a);
    CPIntVar sb = element(sq, b);
    CPIntVar sc = element(sq, c);
    CPIntVar sd = element(sq, d);
    m.cp().post(eq(sum(sa, sb), sum(sc, sd)));

    out.put("a", a);
    out.put("b", b);
    out.put("c", c);
    out.put("d", d);
  }
}
