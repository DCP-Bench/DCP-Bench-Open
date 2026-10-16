import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Peculiar numbers: find a number n in 1..10000, other than 48, such that n + 1 is a
// square and (n / 2) + 1 is a square. The instance has no fields.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the number itself, and its half (n is even, so the half is exact)
    IntVar peculiar = m.intVar("peculiar", 1, 10000);
    IntVar half = m.intVar("half", 1, 5000);
    // peculiar = 2 * half
    m.arithm(peculiar, "=", half, "*", 2).post();

    // "another number": not the 48 of the statement
    m.arithm(peculiar, "!=", 48).post();

    // adding 1 to the number gives a square: peculiar + 1 = a * a
    IntVar plusOne = m.intVar("peculiar_plus_1", 2, 10001);
    IntVar a = m.intVar("a", 1, 100);
    m.arithm(plusOne, "-", peculiar, "=", 1).post();
    m.square(plusOne, a).post();

    // adding 1 to its half gives a square: half + 1 = b * b
    IntVar halfPlusOne = m.intVar("half_plus_1", 2, 5001);
    IntVar b = m.intVar("b", 1, 70);
    m.arithm(halfPlusOne, "-", half, "=", 1).post();
    m.square(halfPlusOne, b).post();

    out.put("peculiar", peculiar);
  }
}
