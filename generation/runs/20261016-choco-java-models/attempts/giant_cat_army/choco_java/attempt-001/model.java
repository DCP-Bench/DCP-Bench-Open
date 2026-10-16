import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Giant cat army game: build a list of 24 integers that starts with 0 and ends with 14,
// where each element is the previous one plus 5, plus 7, or the square root of the previous one,
// all elements are distinct integers <= 60, and 2, 10 and 14 appear in that order.
public class Submission {
  static final int LENGTH = 24, MAX = 60;

  public static void build(Instance inst, Model m, Outputs out) {
    // x[i] = i-th number of the list
    IntVar[] x = m.intVarArray("x", LENGTH, 0, MAX);

    // the list starts with 0 and ends with 14
    m.arithm(x[0], "=", 0).post();
    m.arithm(x[LENGTH - 1], "=", 14).post();

    // all elements are distinct
    m.allDifferent(x, "AC").post();

    // each step adds 5, adds 7, or takes the square root (only when the previous number is a perfect square)
    Tuples moves = new Tuples(true);
    for (int v = 0; v <= MAX; v++) {
      if (v + 5 <= MAX) moves.add(v, v + 5);
      if (v + 7 <= MAX) moves.add(v, v + 7);
      int r = (int) Math.round(Math.sqrt(v));
      if (r * r == v) moves.add(v, r);
    }
    for (int i = 1; i < LENGTH; i++) {
      m.table(new IntVar[]{x[i - 1], x[i]}, moves).post();
    }

    // 2, 10 and 14 appear on the list in that order, other numbers may lie between them
    BoolVar[] is2 = new BoolVar[LENGTH];
    BoolVar[] is10 = new BoolVar[LENGTH];
    for (int i = 0; i < LENGTH; i++) {
      is2[i] = x[i].eq(2).boolVar();
      is10[i] = x[i].eq(10).boolVar();
    }
    // seen2[i] = 1 if the number 2 appears at or before position i
    BoolVar[] seen2 = new BoolVar[LENGTH];
    seen2[0] = is2[0];
    for (int i = 1; i < LENGTH; i++) {
      seen2[i] = m.boolVar("seen2_" + i);
      // seen2[i] = seen2[i-1] or is2[i]
      m.arithm(seen2[i], ">=", seen2[i - 1]).post();
      m.arithm(seen2[i], ">=", is2[i]).post();
      m.sum(new BoolVar[]{seen2[i - 1], is2[i]}, ">=", seen2[i]).post();
    }
    // 2 appears before the end, and 10 appears only after an earlier 2
    m.arithm(seen2[LENGTH - 2], "=", 1).post();
    for (int j = 1; j < LENGTH - 1; j++) {
      m.arithm(is10[j], "<=", seen2[j - 1]).post();
    }
    m.sum(is10, ">=", 1).post();

    out.put("x", x);
  }
}
