// Abbot's puzzle: 100 bushels of corn are distributed among 100 people.
// Each man gets three bushels, each woman two, each child half a bushel.
// There are five times as many women as men. Find the number of men,
// women and children.

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the problem fixes 100 bushels and 100 people (no instance data)
    // number of men, women and children, each between 0 and 100 people
    CPIntVar men = m.intVar(0, 100);
    CPIntVar women = m.intVar(0, 100);
    CPIntVar children = m.intVar(0, 100);

    // there are five times as many women as men
    m.cp().post(eq(women, mul(men, 5)));

    // every person is a man, a woman or a child
    // (100 people in total)
    m.cp().post(eq(sum(men, women, children), 100));

    // the 100 bushels of corn are distributed exactly
    // (each man 3 bushels, each woman 2, each child 1/2 bushel).
    // Counted in half bushels, to stay in integers: 6 per man, 4 per woman,
    // 1 per child, and the total is 200 half bushels.
    m.cp().post(eq(sum(mul(men, 6), mul(women, 4), children), 200));

    out.put("men", men);
    out.put("women", women);
    out.put("children", children);
  }
}
