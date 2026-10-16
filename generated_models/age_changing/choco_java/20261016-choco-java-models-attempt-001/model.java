import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.Constraint;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.constraints.extension.Tuples;
import dcp.Instance;
import dcp.Outputs;

// Age puzzle: starting from my age m and applying the operations +2, /8, -3, *7 in some
// order gives the husband's age h. Starting from h and applying the same four operations
// in a different order gives m. Find m and h.
public class Submission {

  // Operation codes: 0 = add 2, 1 = divide by 8 (exact), 2 = subtract 3, 3 = multiply by 7.
  static final int ADD = 0, DIV = 1, SUB = 2, MUL = 3;
  // Ages are non-negative integers; this upper bound is a generous assumption, not from the statement.
  static final int MAX_AGE = 2000;

  // Allowed (operation, input age, output age) triples, as a table for one step.
  static Tuples stepTable() {
    Tuples t = new Tuples(true);
    for (int x = 0; x <= MAX_AGE; x++) {
      if (x + 2 <= MAX_AGE) t.add(ADD, x, x + 2);          // +2
      if (x % 8 == 0) t.add(DIV, x, x / 8);                 // /8 only when it divides exactly
      if (x >= 3) t.add(SUB, x, x - 3);                     // -3 keeps the age non-negative
      if (7 * x <= MAX_AGE) t.add(MUL, x, 7 * x);           // *7
    }
    return t;
  }

  public static void build(Instance inst, Model m, Outputs out) {
    Tuples step = stepTable();

    IntVar my = m.intVar("m", 0, MAX_AGE);       // my age
    IntVar his = m.intVar("h", 0, MAX_AGE);      // husband's age

    // Sequence A: my age, then the four operations in some order, gives the husband's age.
    IntVar[] opA = m.intVarArray("opA", 4, 0, 3);  // operation applied at each step
    IntVar[] ageA = m.intVarArray("ageA", 5, 0, MAX_AGE);
    // each of the four operations is used exactly once
    m.allDifferent(opA, "AC").post();
    m.arithm(ageA[0], "=", my).post();
    m.arithm(ageA[4], "=", his).post();
    for (int k = 0; k < 4; k++) {
      m.table(new IntVar[]{opA[k], ageA[k], ageA[k + 1]}, step).post();
    }

    // Sequence B: the husband's age, then the same four operations in some order, gives my age.
    IntVar[] opB = m.intVarArray("opB", 4, 0, 3);
    IntVar[] ageB = m.intVarArray("ageB", 5, 0, MAX_AGE);
    // each of the four operations is used exactly once
    m.allDifferent(opB, "AC").post();
    m.arithm(ageB[0], "=", his).post();
    m.arithm(ageB[4], "=", my).post();
    for (int k = 0; k < 4; k++) {
      m.table(new IntVar[]{opB[k], ageB[k], ageB[k + 1]}, step).post();
    }

    // the two sequences apply the operations in a different order
    Constraint[] differentSlot = new Constraint[4];
    for (int k = 0; k < 4; k++) differentSlot[k] = m.arithm(opA[k], "!=", opB[k]);
    m.or(differentSlot).post();

    out.put("m", my);
    out.put("h", his);
  }
}
