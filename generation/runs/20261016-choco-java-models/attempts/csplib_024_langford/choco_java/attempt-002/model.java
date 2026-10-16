import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Langford pairing: arrange two copies of each number 1..k in one sequence of 2k
// positions so that the two copies of i are exactly i+1 positions apart.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int k = inst.getInt("k");
    int len = 2 * k;

    // first[i-1]: position of the first copy of number i; second[i-1]: position of the second copy
    IntVar[] first = new IntVar[k];
    IntVar[] second = new IntVar[k];
    for (int i = 1; i <= k; i++) {
      // the first copy fits, with room for the second copy i+1 positions later
      first[i - 1] = m.intVar("first" + i, 0, len - 2 - i);
      second[i - 1] = m.intVar("second" + i, i + 1, len - 1);
      // the second copy of i sits i+1 positions after the first copy
      m.arithm(second[i - 1], "-", first[i - 1], "=", i + 1).post();
    }

    // every position holds exactly one number: all 2k copy positions are different
    IntVar[] positions = new IntVar[len];
    for (int i = 0; i < k; i++) {
      positions[2 * i] = first[i];
      positions[2 * i + 1] = second[i];
    }
    m.allDifferent(positions, "DEFAULT").post();

    // the sequence itself: sol[p] is the number that sits at position p
    IntVar[] sol = m.intVarArray("sol", len, 1, k);
    for (int i = 1; i <= k; i++) {
      // the first and second copy of i both hold the number i
      m.element(m.intVar(i), sol, first[i - 1], 0).post();
      m.element(m.intVar(i), sol, second[i - 1], 0).post();
    }

    out.put("sol", sol);
  }
}
