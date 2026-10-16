import java.util.ArrayList;
import java.util.List;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// My age m and my husband's age h. Four operations, each used exactly once, in some order:
// +2, /8, -3, *7. Applying them in one order to my age gives his age; applying them
// in a different order to his age gives my age.
// The problem has no instance data, so the model reads nothing from the instance.
public class Submission {

  // Ages are taken between 0 and 150. Intermediate values of a chain may go negative
  // (for example 0 - 3 before a multiplication), so they range over -BOUND..BOUND.
  // Starting from an age in 0..150 the largest intermediate value is 7 * (150 + 5) = 1085.
  static final int AGE_MAX = 150;
  static final int BOUND = 1100;

  // The operation codes used in the step variables.
  static final int ADD2 = 0, DIV8 = 1, SUB3 = 2, MUL7 = 3;

  public static void build(Instance inst, Model m, Outputs out) {
    // Each row is (operation, value before, value after). A division by 8 is only
    // allowed when it is exact, since ages are whole numbers.
    int[][] rows = stepRows();

    CPIntVar myAge = m.intVar(0, AGE_MAX);
    CPIntVar husbandAge = m.intVar(0, AGE_MAX);

    // the order in which my age is changed into his age
    CPIntVar[] order = m.intVarArray(4, 0, 3);
    // the order in which his age is changed into mine
    CPIntVar[] reverse = m.intVarArray(4, 0, 3);

    // each of the four operations is used once in each order
    m.cp().post(allDifferent(order));
    m.cp().post(allDifferent(reverse));

    // applying the order to my age gives his age
    chain(m, myAge, husbandAge, order, rows);
    // applying the second order to his age gives my age
    chain(m, husbandAge, myAge, reverse, rows);

    // the second order is a different order from the first: the two codes differ
    CPIntVar orderCode = sum(new CPIntVar[]{order[0], mul(order[1], 4), mul(order[2], 16), mul(order[3], 64)});
    CPIntVar reverseCode = sum(new CPIntVar[]{reverse[0], mul(reverse[1], 4), mul(reverse[2], 16), mul(reverse[3], 64)});
    m.cp().post(neq(orderCode, reverseCode));

    out.put("m", myAge);
    out.put("h", husbandAge);
  }

  // Posts a chain of four operations from start to end. Step k applies ops[k].
  static void chain(Model m, CPIntVar start, CPIntVar end, CPIntVar[] ops, int[][] rows) {
    CPIntVar[] values = new CPIntVar[5];
    values[0] = start;
    for (int k = 0; k < 4; k++) {
      values[k + 1] = (k == 3) ? end : m.intVar(-BOUND, BOUND);
      m.cp().post(table(new CPIntVar[]{ops[k], values[k], values[k + 1]}, rows));
    }
  }

  // Every (operation, before, after) triple whose result stays within -BOUND..BOUND.
  static int[][] stepRows() {
    List<int[]> rows = new ArrayList<>();
    for (int v = -BOUND; v <= BOUND; v++) {
      // +2
      if (v + 2 <= BOUND) rows.add(new int[]{ADD2, v, v + 2});
      // /8, exact division only
      if (v % 8 == 0) rows.add(new int[]{DIV8, v, v / 8});
      // -3
      if (v - 3 >= -BOUND) rows.add(new int[]{SUB3, v, v - 3});
      // *7
      if (Math.abs(7L * v) <= BOUND) rows.add(new int[]{MUL7, v, 7 * v});
    }
    return rows.toArray(new int[0][]);
  }
}
