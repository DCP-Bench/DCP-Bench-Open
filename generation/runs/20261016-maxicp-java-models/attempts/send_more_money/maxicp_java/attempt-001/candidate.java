// SEND + MORE = MONEY: each letter stands for a distinct digit from 0 to 9,
// the first letters of SEND and MORE are not zero, and the sum holds.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // each letter stands for a digit from 0 to 9
    CPIntVar S = m.intVar(0, 9);
    CPIntVar E = m.intVar(0, 9);
    CPIntVar N = m.intVar(0, 9);
    CPIntVar D = m.intVar(0, 9);
    CPIntVar M = m.intVar(0, 9);
    CPIntVar O = m.intVar(0, 9);
    CPIntVar R = m.intVar(0, 9);
    CPIntVar Y = m.intVar(0, 9);

    // each letter is a different digit
    m.cp().post(allDifferent(new CPIntVar[] {S, E, N, D, M, O, R, Y}));

    // the first letter of each word is not zero
    m.cp().post(neq(S, 0));
    m.cp().post(neq(M, 0));

    // SEND + MORE = MONEY, written as one linear equation
    CPIntVar send = sum(new CPIntVar[] {mul(S, 1000), mul(E, 100), mul(N, 10), D});
    CPIntVar more = sum(new CPIntVar[] {mul(M, 1000), mul(O, 100), mul(R, 10), E});
    CPIntVar money = sum(new CPIntVar[] {mul(M, 10000), mul(O, 1000), mul(N, 100), mul(E, 10), Y});
    // the sum of SEND and MORE equals MONEY
    m.cp().post(eq(sum(new CPIntVar[] {send, more}), money));

    out.put("d", D);
    out.put("e", E);
    out.put("m", M);
    out.put("n", N);
    out.put("o", O);
    out.put("r", R);
    out.put("s", S);
    out.put("y", Y);
  }
}
