// Hanging weights puzzle: weights A-M hang from a system of bars. Each weight is an
// integer in 1..13. Every bar balances: the weights on either side of its pivot,
// weighted by distance from the pivot, are equal. A bar hanging beneath another
// contributes its total weight as one weight.

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // each weight has an integer value between 1 and 13
    CPIntVar a = m.intVar(1, 13);
    CPIntVar b = m.intVar(1, 13);
    CPIntVar c = m.intVar(1, 13);
    CPIntVar d = m.intVar(1, 13);
    CPIntVar e = m.intVar(1, 13);
    CPIntVar f = m.intVar(1, 13);
    CPIntVar g = m.intVar(1, 13);
    CPIntVar h = m.intVar(1, 13);
    CPIntVar i = m.intVar(1, 13);
    CPIntVar j = m.intVar(1, 13);
    CPIntVar k = m.intVar(1, 13);
    CPIntVar l = m.intVar(1, 13);
    CPIntVar mm = m.intVar(1, 13);

    // bottom right bar: 5*C = D (C is 5 from the pivot, D is 1 from the pivot)
    m.cp().post(eq(mul(c, 5), d));

    // the bar above it: 3*G = 2*(C+D)
    m.cp().post(eq(mul(g, 3), mul(sum(c, d), 2)));

    // bottom left bar (A, B): 4*A = B
    m.cp().post(eq(mul(a, 4), b));

    // bar carrying E and F: 3*E = 2*F
    m.cp().post(eq(mul(e, 3), mul(f, 2)));

    // bar carrying H, I and the bar E-F: 3*H = 2*(E+F) + 3*I
    m.cp().post(eq(mul(h, 3), sum(mul(sum(e, f), 2), mul(i, 3))));

    // bar carrying L and M, hung from H-I bar on one side: (H+I+E+F) = L + 4*M
    m.cp().post(eq(sum(new CPIntVar[]{h, i, e, f}), sum(new CPIntVar[]{l, mul(mm, 4)})));

    // bar carrying J and K, with the A-B bar on its left and the G bar on its right:
    // 2*J + 3*(A+B) = K + 2*(G+C+D)
    m.cp().post(eq(sum(new CPIntVar[]{mul(j, 2), mul(sum(a, b), 3)}),
                   sum(new CPIntVar[]{k, mul(sum(new CPIntVar[]{g, c, d}), 2)})));

    // top bar: the L-M bar (total H+I+E+F+L+M) at distance 4 and the J-K bar at distance 3
    m.cp().post(eq(mul(sum(new CPIntVar[]{h, i, e, f, l, mm}), 4),
                   mul(sum(new CPIntVar[]{j, k, a, b, g, c, d}), 3)));

    out.put("a", a);
    out.put("b", b);
    out.put("c", c);
    out.put("d", d);
    out.put("e", e);
    out.put("f", f);
    out.put("g", g);
    out.put("h", h);
    out.put("i", i);
    out.put("j", j);
    out.put("k", k);
    out.put("l", l);
    out.put("m", mm);
  }
}
