import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Dinner: take 1-6 grandparents, 1-10 parents and 1-40 children to dinner.
// There must be 20 people in total, and the dinner must cost $20.
// Grandparents cost $3, parents $2 and children $0.50.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // we take 1-6 grandparents
    CPIntVar grandparents = m.intVar(1, 6);
    // we take 1-10 parents
    CPIntVar parents = m.intVar(1, 10);
    // we take 1-40 children
    CPIntVar children = m.intVar(1, 40);

    // there must be 20 total people at dinner
    m.cp().post(eq(sum(grandparents, parents, children), 20));

    // it must cost $20: $3, $2 and $0.50 per person, so in half-dollars
    // 6 per grandparent, 4 per parent, 1 per child, total 40
    m.cp().post(eq(sum(mul(grandparents, 6), mul(parents, 4), children), 40));

    out.put("grandparents", grandparents);
    out.put("parents", parents);
    out.put("children", children);
  }
}
