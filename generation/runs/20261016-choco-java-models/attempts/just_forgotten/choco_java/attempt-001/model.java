import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Just forgotten: find Joe's account number, a permutation x of the digits 0..n-1, such that
// each set of digits has exactly num_correct_digits digits in the same position as x.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] sets = inst.getIntMatrix("sets");
    int k = inst.getInt("num_correct_digits");
    int n = sets[0].length;

    // The account number has all digits from 0 to n-1, in some order
    IntVar[] x = m.intVarArray("x", n, 0, n - 1);
    m.allDifferent(x, "AC").post();

    // In each set, exactly k digits are in their correct position
    for (int[] set : sets) {
      BoolVar[] correct = new BoolVar[n];
      for (int i = 0; i < n; i++) {
        // position i is correct when the account number has the set's digit there
        correct[i] = x[i].eq(set[i]).boolVar();
      }
      m.sum(correct, "=", k).post();
    }

    out.put("x", x);
  }
}
