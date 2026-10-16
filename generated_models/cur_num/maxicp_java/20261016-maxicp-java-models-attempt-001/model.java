// The number 48 has this peculiarity: if you add 1 to it, the result is a
// square number, and if you add 1 to its half, you also get a square number.
// Print another number with this peculiarity between 1 and 10000.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // a number with this peculiarity, between 1 and 10000
    CPIntVar peculiar = m.intVar(1, 10000);
    // print another number, so not 48
    m.cp().post(neq(peculiar, 48));

    // its half: the number is even, and half is the number divided by 2
    CPIntVar half = m.intVar(1, 5000);
    m.cp().post(eq(peculiar, mul(half, 2)));

    // if you add 1 to the number, the result is a square number
    int[] squares = new int[102];
    for (int k = 0; k <= 101; k++) squares[k] = k * k;
    CPIntVar a = m.intVar(0, 101);
    m.cp().post(eq(plus(peculiar, 1), element(squares, a)));

    // if you add 1 to its half, you also get a square number
    int[] squaresHalf = new int[71];
    for (int k = 0; k <= 70; k++) squaresHalf[k] = k * k;
    CPIntVar b = m.intVar(0, 70);
    m.cp().post(eq(plus(half, 1), element(squaresHalf, b)));

    out.put("peculiar", peculiar);
  }
}
