import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// ISBN-13: fill the unknown digits (-1 in the input) so that the 13 digits form a
// valid ISBN-13 that starts with 978 or 979.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] init = inst.getIntArray("isbn_init");   // -1 = unknown digit, otherwise the given digit
    int n = init.length;                          // 13

    // the 13 digits of the ISBN, each a digit from 0 to 9
    IntVar[] isbn = m.intVarArray("isbn", n, 0, 9);

    // the given digits are kept
    for (int i = 0; i < n; i++) {
      if (init[i] != -1) isbn[i].eq(init[i]).post();
    }

    // the number starts with 978 or 979
    m.arithm(isbn[0], "=", 9).post();
    m.arithm(isbn[1], "=", 7).post();
    m.arithm(isbn[2], ">=", 8).post();

    // multiply the digits alternately by 1 and 3 (starting with 1) and sum the products;
    // the check digit makes this sum a multiple of 10
    int[] weight = new int[n];
    for (int i = 0; i < n; i++) weight[i] = (i % 2 == 0) ? 1 : 3;
    IntVar total = m.intVar("weighted sum", 0, 9 * 2 * n, true);
    m.scalar(isbn, weight, "=", total).post();

    // the weighted sum is a multiple of 10: (10 - sum % 10) % 10 equals the check digit
    total.mod(10).eq(0).post();

    out.put("isbn", isbn);
  }
}
