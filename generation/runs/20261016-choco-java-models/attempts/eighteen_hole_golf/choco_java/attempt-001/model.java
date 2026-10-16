import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Eighteen-hole golf course: choose the length of each of 18 holes, each 3, 4 or 5,
// so that the total length of the course is 72. The instance has no fields.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int holes = 18;
    // length of hole i, one of 3, 4 or 5
    IntVar[] length = m.intVarArray("hole", holes, new int[]{3, 4, 5});

    // the total length of the course is 72
    m.sum(length, "=", 72).post();

    out.put("holes", length);
  }
}
