import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

// Three sum (generalised): choose m of the given integers so that the chosen ones sum to zero.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] nums = inst.getIntArray("nums");
    int count = inst.getInt("m");
    int n = nums.length;

    // indices[i] = 1 if element i is selected
    BoolVar[] indices = m.boolVarArray("indices", n);

    // exactly m elements are selected
    m.sum(indices, "=", count).post();

    // the selected elements sum to zero
    m.scalar(indices, nums, "=", 0).post();

    out.put("indices", indices);
  }
}
