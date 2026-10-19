import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Climbing stairs: a stair of n steps is climbed with moves of m1 to m2 steps each.
// steps[k] is the size of the k-th move, or 0 once the top is reached.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the number of steps of the stair
    int n = inst.getInt("n");
    // the smallest and the largest number of steps in one move
    int m1 = inst.getInt("m1");
    int m2 = inst.getInt("m2");

    // the moves: at most n moves (each takes at least one step), each between 0 and m2 steps
    CPIntVar[] steps = m.intVarArray(n, 0, m2);
    // zero[k] = 1 if no steps are taken at move k (the top has been reached)
    CPBoolVar[] zero = new CPBoolVar[n];
    for (int k = 0; k < n; k++) {
      zero[k] = isEq(steps[k], 0);
    }

    // each move takes between m1 and m2 steps, or none after the top is reached
    int[][] allowed = new int[m2 - m1 + 2][];
    int row = 0;
    for (int v = m1; v <= m2; v++) {
      allowed[row++] = new int[] {v, 0};
    }
    allowed[row] = new int[] {0, 1};
    for (int k = 0; k < n; k++) {
      m.cp().post(table(new CPIntVar[] {steps[k], zero[k]}, allowed));
    }

    // once the top is reached, every later move takes no steps
    for (int k = 0; k + 1 < n; k++) {
      m.cp().post(implies(zero[k], zero[k + 1]));
    }

    // the moves together climb exactly the n steps of the stair
    m.cp().post(sum(steps, n));

    out.put("steps", steps);
  }
}
