import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Dinner headcount: choose how many grandparents, parents and children go to dinner
// so that 20 people attend and the bill is exactly $20.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // at most 6 grandparents, 10 parents and 40 children, at least one of each kind
    IntVar grandparents = m.intVar("grandparents", 1, 6);
    IntVar parents = m.intVar("parents", 1, 10);
    IntVar children = m.intVar("children", 1, 40);

    // there must be 20 total people at dinner
    m.sum(new IntVar[]{grandparents, parents, children}, "=", 20).post();

    // the dinner must cost $20; costs are in cents: grandparents $3, parents $2, children $0.50
    m.scalar(new IntVar[]{grandparents, parents, children}, new int[]{300, 200, 50}, "=", 2000).post();

    out.put("grandparents", grandparents);
    out.put("parents", parents);
    out.put("children", children);
  }
}
