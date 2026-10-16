import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// SEND + MORE = MONEY: assign a distinct digit to each letter so that the sum holds,
// with no leading zero in SEND or MORE.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // each letter is a digit 0..9 (problem-given domain); the leading letters s and m are 1..9
    IntVar s = m.intVar("s", 1, 9);
    IntVar e = m.intVar("e", 0, 9);
    IntVar n = m.intVar("n", 0, 9);
    IntVar d = m.intVar("d", 0, 9);
    IntVar mm = m.intVar("m", 1, 9);
    IntVar o = m.intVar("o", 0, 9);
    IntVar r = m.intVar("r", 0, 9);
    IntVar y = m.intVar("y", 0, 9);
    IntVar[] letters = {s, e, n, d, mm, o, r, y};

    // every letter stands for a different digit
    m.allDifferent(letters, "AC").post();

    // the three words as numbers: SEND, MORE and MONEY
    IntVar send = m.intVar("SEND", 1000, 9999, true);
    IntVar more = m.intVar("MORE", 1000, 9999, true);
    IntVar money = m.intVar("MONEY", 10000, 99999, true);
    m.scalar(new IntVar[]{s, e, n, d}, new int[]{1000, 100, 10, 1}, "=", send).post();
    m.scalar(new IntVar[]{mm, o, r, e}, new int[]{1000, 100, 10, 1}, "=", more).post();
    m.scalar(new IntVar[]{mm, o, n, e, y}, new int[]{10000, 1000, 100, 10, 1}, "=", money).post();

    // SEND + MORE = MONEY
    m.arithm(send, "+", more, "=", money).post();

    out.put("d", d);
    out.put("e", e);
    out.put("m", mm);
    out.put("n", n);
    out.put("o", o);
    out.put("r", r);
    out.put("s", s);
    out.put("y", y);
  }
}
