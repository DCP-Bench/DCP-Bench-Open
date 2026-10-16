// A boy passes through num_gates gates to give an apple to a girl. Each gate has a guard.
// At each gate he gives the guard half of his apples plus one, as an integer number of apples.
// After the last gate he has 1 apple left, which he gives to the girl.
// apples[i] = apples before gate i; apples[num_gates] = apples after the last gate.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int gates = inst.getInt("num_gates");

    // Bound on apples[0]: working back from 1 apple after the last gate,
    // each gate maps a count a to a/2 - 1, so a = 2 * (count after the gate + 1).
    // Starting from 1 this gives 3 * 2^gates - 2 before the first gate.
    int top = 3 * (1 << gates) - 2;

    CPIntVar[] apples = m.intVarArray(gates + 1, 0, top);

    // he has 1 apple left after the last gate, which he gives to the girl
    m.cp().post(eq(apples[gates], 1));

    for (int g = 0; g < gates; g++) {
      // the guard's share is half of his apples, so the apples before the gate are even
      CPIntVar half = m.intVar(0, top / 2);
      m.cp().post(eq(mul(half, 2), apples[g]));

      // the bribe to the guard is half of his apples, plus one
      CPIntVar bribe = m.intVar(1, top / 2 + 1);
      m.cp().post(eq(bribe, plus(half, 1)));

      // after the bribe he keeps the rest of his apples
      m.cp().post(sum(new CPIntVar[] {apples[g + 1], bribe}, apples[g]));
    }

    out.put("apples", apples);
  }
}
