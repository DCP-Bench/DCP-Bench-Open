import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.constraints.extension.Tuples;
import dcp.Instance;
import dcp.Outputs;

// Dinner seating: six guests around a round table, seated so that no two guests
// who do not get along sit next to each other (zero conflicts).
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // guests: 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank
    // x[s] = guest sitting in seat s (seats 0..5 around the table)
    IntVar[] x = m.intVarArray("x", 6, 0, 5);
    m.allDifferent(x, "AC").post();

    // each guest sits only next to the guests they get along with (both directions)
    int[][] allowed = {
      {0, 3}, {0, 5},  // Andrew: Dave, Frank
      {1, 2}, {1, 4},  // Betty: Cara, Erica
      {2, 1}, {2, 5},  // Cara: Betty, Frank
      {3, 0}, {3, 4},  // Dave: Andrew, Erica
      {4, 1}, {4, 3},  // Erica: Betty, Dave
      {5, 0}, {5, 2}   // Frank: Andrew, Cara
    };
    Tuples pairs = new Tuples(true);
    for (int[] p : allowed) pairs.add(p);

    // seats s and s+1 (and seat 5 next to seat 0, round table) must hold a compatible pair
    for (int s = 0; s < 6; s++) {
      m.table(x[s], x[(s + 1) % 6], pairs).post();
    }

    out.put("x", x);
  }
}
