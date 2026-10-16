import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Among: choose the entries of an array x of length n, each between 0 and 7, so that
// exactly m of them take a value from the set v.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int count = inst.getInt("m");
    int[] v = inst.getIntArray("v");
    IntVar[] x = m.intVarArray("x", n, 0, 7);  // every entry takes a value from 0 to 7

    // exactly m entries of x take a value in v
    m.among(m.intVar(count), x, v).post();

    out.put("x", x);
  }
}
