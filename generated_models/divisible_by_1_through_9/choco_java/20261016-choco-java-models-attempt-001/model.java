import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Find a 10 digit number that uses each digit 0 to 9 exactly once, where the number
// formed by its first n digits is divisible by n, for every n from 1 to 10.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // d[i] is the digit at position i, read from left to right
    IntVar[] d = m.intVarArray("d", 10, 0, 9);

    // the number uses each of the digits 0 to 9 exactly once
    m.allDifferent(d, "AC").post();

    // the number has 10 digits, so it does not start with 0
    d[0].ne(0).post();

    // the number formed by the first n digits is divisible by n.
    // The prefix is too large for Choco's integer bounds, so its remainder modulo n is
    // carried digit by digit: r = (10 * r + next digit) mod n. The prefix is divisible
    // by n when the final remainder is 0.
    for (int n = 1; n <= 10; n++) {
      // remainder of the first digit modulo n
      IntVar r = m.intVar(0, n - 1);
      m.mod(d[0], n, r).post();
      for (int len = 2; len <= n; len++) {
        // extend the prefix by one digit: 10 * previous remainder + next digit
        IntVar shifted = r.mul(10).add(d[len - 1]).intVar();
        IntVar next = m.intVar(0, n - 1);
        m.mod(shifted, n, next).post();
        r = next;
      }
      // the first n digits leave no remainder when divided by n
      m.arithm(r, "=", 0).post();
    }

    out.putDigits("number", d, 10);
  }
}
