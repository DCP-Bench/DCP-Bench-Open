import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// The set {1, 3, 8, 120} has the property that the product of any two members is one less
// than a perfect square. Find a fifth number number >= 0 that keeps the property.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the members of the given set, from the statement
    int[] members = {1, 3, 8, 120};
    // the search range for the fifth number comes from the instance
    int maxVal = inst.getInt("max_val");

    IntVar number = m.intVar("number", 0, maxVal);

    // the fifth number is a new member, so it differs from each given member
    for (int a : members) {
      number.ne(a).post();
    }

    // the product of the fifth number and each member is one less than a perfect square:
    // a * number + 1 = root_a * root_a
    int maxProduct = 120 * maxVal + 1;
    int maxRoot = (int) Math.ceil(Math.sqrt(maxProduct)) + 1;
    for (int a : members) {
      IntVar product = number.mul(a).add(1).intVar();
      IntVar root = m.intVar("root_" + a, 0, maxRoot);
      IntVar square = m.intVar("square_" + a, 0, maxRoot * maxRoot, true);
      m.times(root, root, square).post();
      square.eq(product).post();
    }

    out.put("number", number);
  }
}
