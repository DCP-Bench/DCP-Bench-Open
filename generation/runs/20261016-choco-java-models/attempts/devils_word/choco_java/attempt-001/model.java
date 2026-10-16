import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Devil's word: given an array of integers, insert '+' or '-' before each integer so
// that the signed sum is the target total. Output the signed array.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] arr = inst.getIntArray("arr");   // the numbers, in order
    int total = inst.getInt("total");      // the target sum (666 in the description)
    int n = arr.length;

    // result[i] is arr[i] with a plus or a minus sign in front
    IntVar[] result = new IntVar[n];
    for (int i = 0; i < n; i++) {
      int a = arr[i];
      result[i] = (a == 0) ? m.intVar("result" + i, 0)
          : m.intVar("result" + i, new int[]{-a, a});
    }

    // summing the signed numbers gives the target total
    m.sum(result, "=", total).post();

    out.put("result", result);
  }
}
