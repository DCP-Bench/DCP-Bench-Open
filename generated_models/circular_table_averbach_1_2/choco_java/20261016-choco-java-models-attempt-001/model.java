import org.chocosolver.solver.Model;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Circular table: three players X, Y, Z sit around a round table with seats 0, 1, 2
// (seat 1 is right of seat 0, seat 2 right of seat 1, seat 0 right of seat 2). Each player
// has a nationality (American, English, French). Determine the seat and nationality of each.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the three players X, Y, Z take the three seats, all different
    IntVar x = m.intVar("x", 0, 2);
    IntVar y = m.intVar("y", 0, 2);
    IntVar z = m.intVar("z", 0, 2);
    m.allDifferent(new IntVar[]{x, y, z}, "AC").post();

    // the three nationalities are held by the three seats, all different
    IntVar american = m.intVar("american", 0, 2);
    IntVar english = m.intVar("english", 0, 2);
    IntVar french = m.intVar("french", 0, 2);
    m.allDifferent(new IntVar[]{american, english, french}, "AC").post();

    // Y passed three hearts to the American: the American sits on the right of Y
    Tuples rightOf = new Tuples(true);
    rightOf.add(0, 1);
    rightOf.add(1, 2);
    rightOf.add(2, 0);
    m.table(new IntVar[]{y, american}, rightOf).post();

    // X passed the queen of spades and two diamonds to the person who passed their cards to
    // the Frenchwoman: X sits on the right of that person, who sits on the left of the Frenchwoman,
    // so the Frenchwoman sits two seats to the right of X
    Tuples twoRightOf = new Tuples(true);
    twoRightOf.add(0, 2);
    twoRightOf.add(1, 0);
    twoRightOf.add(2, 1);
    m.table(new IntVar[]{x, french}, twoRightOf).post();

    out.put("x", x);
    out.put("y", y);
    out.put("z", z);
    out.put("american", american);
    out.put("english", english);
    out.put("french", french);
  }
}
