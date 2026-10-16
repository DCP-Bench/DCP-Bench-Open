// Given a collection of integers, find a number of elements that sum to zero.
// Print whether each element is selected (indices) as a list of booleans.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the collection of integers
    int[] nums = inst.getIntArray("nums");
    // the number of elements to select
    int k = inst.getInt("m");
    int n = nums.length;

    // indices[i] = 1 if element i is selected
    CPBoolVar[] indices = m.boolVarArray(n);

    // exactly m elements are selected
    m.cp().post(sum(indices, k));

    // the selected elements sum to zero
    CPIntVar[] terms = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      terms[i] = mul(indices[i], nums[i]);
    }
    CPIntVar total = sum(terms);
    m.cp().post(eq(total, 0));

    out.put("indices", indices);
  }
}
