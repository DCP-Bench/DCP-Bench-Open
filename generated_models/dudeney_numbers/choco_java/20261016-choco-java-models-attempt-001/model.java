import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Dudeney number: a perfect cube whose digit sum equals its cube root, here larger than 1
// and written with at most n digits.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");
    int maxNumber = (int) Math.pow(10, n) - 1;

    // digits of the number, most significant last; leading zeros are allowed
    IntVar[] digits = m.intVarArray("digit", n, 0, 9);
    int[] weights = new int[n];
    for (int i = 0; i < n; i++) weights[i] = (int) Math.pow(10, i);

    IntVar number = m.intVar("number", 0, maxNumber, true);
    m.scalar(digits, weights, "=", number).post();

    // the cube root is the digit sum of the number
    IntVar root = m.intVar("root", 0, 9 * n, true);
    m.sum(digits, "=", root).post();

    // the number is a perfect cube: number = root^3
    m.pow(root, 3, number).post();

    // the number is larger than 1
    m.arithm(number, ">", 1).post();

    out.put("number", number);
  }
}
