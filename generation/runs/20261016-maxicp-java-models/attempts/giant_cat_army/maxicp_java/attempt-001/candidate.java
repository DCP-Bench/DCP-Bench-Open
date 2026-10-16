// Giant cat army: build a list of 24 distinct integers, each at most 60, starting at 0 and ending at 14.
// Each step adds 5, adds 7, or takes the square root (only when the result is an integer).
// The list contains 2, 10 and 14 in that order; other numbers may sit between them.
import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int len = 24;      // the list has length 24
    int maxValue = 60; // all elements are <= 60

    CPIntVar[] x = m.intVarArray(len, 0, maxValue);

    // the list starts with 0
    m.cp().post(eq(x[0], 0));
    // and ends with 14
    m.cp().post(eq(x[len - 1], 14));

    // all the elements are distinct
    m.cp().post(allDifferent(x));

    // one of three operations: adding 5, adding 7, or taking the square root
    // (the square root only applies when the result is an integer)
    List<int[]> steps = new ArrayList<>();
    for (int v = 0; v <= maxValue; v++) {
      if (v + 5 <= maxValue) steps.add(new int[]{v, v + 5});
      if (v + 7 <= maxValue) steps.add(new int[]{v, v + 7});
      int r = (int) Math.round(Math.sqrt(v));
      if (r * r == v) steps.add(new int[]{v, r});
    }
    int[][] allowedSteps = steps.toArray(new int[0][]);
    for (int i = 0; i + 1 < len; i++) {
      m.cp().post(table(new CPIntVar[]{x[i], x[i + 1]}, allowedSteps));
    }

    // 2, 10 and 14 appear on the list in that order, other numbers may sit between them
    CPBoolVar[] is2 = new CPBoolVar[len];
    CPBoolVar[] is10 = new CPBoolVar[len];
    for (int i = 0; i < len; i++) {
      is2[i] = isEq(x[i], 2);
      is10[i] = isEq(x[i], 10);
    }
    // 10 is on the list
    m.cp().post(or(is10));
    // every 10 has a 2 before it (position 0 holds 0, so 10 cannot sit there)
    for (int j = 1; j < len; j++) {
      CPBoolVar[] twoBefore = new CPBoolVar[j];
      for (int i = 0; i < j; i++) twoBefore[i] = is2[i];
      m.cp().post(ge(sum(twoBefore), is10[j]));
    }

    out.put("x", x);
  }
}
