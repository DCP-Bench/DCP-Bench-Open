import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Langford's problem: two copies of each number 1..k are arranged in one sequence of
// length 2k, so that the two copies of number i have exactly i numbers between them.
// Output sol lists the sequence position by position, values 1..k.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int k = inst.getInt("k");
    int len = 2 * k;

    // the sequence, one value per position
    CPIntVar[] sol = m.intVarArray(len, 1, k);

    // first[i-1] is the position of the first copy of i, second[i-1] of the second copy
    CPIntVar[] first = new CPIntVar[k];
    CPIntVar[] second = new CPIntVar[k];
    for (int i = 1; i <= k; i++) {
      first[i - 1] = m.intVar(0, len - i - 2);
      second[i - 1] = m.intVar(0, len - 1);
    }

    // the two copies of i appear i numbers apart: second = first + i + 1
    for (int i = 1; i <= k; i++) {
      m.cp().post(eq(plus(first[i - 1], i + 1), second[i - 1]));
    }

    // every position holds exactly one number
    CPIntVar[] positions = new CPIntVar[len];
    for (int i = 0; i < k; i++) {
      positions[2 * i] = first[i];
      positions[2 * i + 1] = second[i];
    }
    m.cp().post(allDifferent(positions));

    // a position taken by a copy of i holds the value i
    for (int i = 1; i <= k; i++) {
      for (int j = 0; j < len; j++) {
        CPBoolVar atFirst = isEq(first[i - 1], j);
        m.cp().post(implies(atFirst, isEq(sol[j], i)));
        CPBoolVar atSecond = isEq(second[i - 1], j);
        m.cp().post(implies(atSecond, isEq(sol[j], i)));
      }
    }

    out.put("sol", sol);
  }
}
