import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// An 18-hole golf course: every hole has a length of 3, 4 or 5,
// and the total length of the course is 72.
// Print the lengths of the holes as a list of 18 integers.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the length of each hole is 3, 4 or 5
    CPIntVar[] holes = m.intVarArray(18, 3, 5);
    // the total length of the course is 72
    m.cp().post(sum(holes, 72));
    out.put("holes", holes);
  }
}
