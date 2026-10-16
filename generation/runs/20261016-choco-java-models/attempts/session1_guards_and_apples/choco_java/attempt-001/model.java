// A boy gives a guard half of his apples plus one at each of num_gates gates. After the last gate
// he has one apple left, which he gives to the girl, so he has none afterwards. Find the number of
// apples before each gate and after the last gate. The boy gives whole apples, so half of his
// apples must be a whole number.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int gates = inst.getInt("num_gates");

    // apples[i] = apples before gate i, apples[gates] = apples after the last gate
    // (the largest count is 3 * 2^gates - 2 when one apple is left at the end; the bound is generous)
    int bound = 1 << (gates + 2);
    IntVar[] apples = new IntVar[gates + 1];
    for (int i = 0; i < gates; i++) apples[i] = m.intVar("apples" + i, 0, bound, true);

    // one apple is left after the last gate: the one he gives the girl
    apples[gates] = m.intVar("apples" + gates, 1);

    // at each gate the boy gives the guard half of his apples plus one, so
    // apples after = apples before / 2 - 1, i.e. 2 * apples after + 2 = apples before
    for (int i = 0; i < gates; i++) {
      m.scalar(new IntVar[]{apples[i], apples[i + 1]}, new int[]{1, -2}, "=", 2).post();
    }

    out.put("apples", apples);
  }
}
