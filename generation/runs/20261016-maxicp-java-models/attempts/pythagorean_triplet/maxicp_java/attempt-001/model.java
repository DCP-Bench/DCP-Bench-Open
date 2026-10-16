// Pythagorean triplet: natural numbers a < b < c with a + b + c = 1000 and a^2 + b^2 = c^2.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the three numbers of the triplet, each a natural number
    CPIntVar a = m.intVar(1, 1000);
    CPIntVar b = m.intVar(1, 1000);
    CPIntVar c = m.intVar(1, 1000);

    // a < b < c (the description's "exactly one triplet" counts the triplet in this order)
    m.cp().post(le(plus(a, 1), b));
    m.cp().post(le(plus(b, 1), c));

    // a + b + c = 1000
    m.cp().post(eq(sum(a, b, c), 1000));

    // squares table: sq[i] = i * i for i in 0..1000 (a fixed mathematical table, not instance data)
    int[] sq = new int[1001];
    for (int i = 0; i <= 1000; i++) sq[i] = i * i;

    // a^2 + b^2 = c^2
    CPIntVar sa = element(sq, a);
    CPIntVar sb = element(sq, b);
    CPIntVar sc = element(sq, c);
    m.cp().post(eq(sum(sa, sb), sc));

    out.put("a", a);
    out.put("b", b);
    out.put("c", c);
  }
}
