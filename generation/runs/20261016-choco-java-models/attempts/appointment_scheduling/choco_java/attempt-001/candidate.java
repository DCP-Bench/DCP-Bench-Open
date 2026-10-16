// Appointment scheduling: assign n people to n interview slots, so that each person gets
// exactly one slot, each slot gets exactly one person, and each person only takes a slot
// in which they are free (free[i][j] = 1). x[i][j] = 1 means person i is assigned slot j.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] free = inst.getIntMatrix("m");   // free[i][j] = 1 if person i is free in slot j
    int n = free.length;                     // people and slots are equal in number

    BoolVar[][] x = m.boolVarMatrix("x", n, n);   // x[i][j]: person i is assigned slot j

    // each person is assigned exactly one slot
    for (int i = 0; i < n; i++) {
      m.sum(x[i], "=", 1).post();
    }

    // each slot is given to exactly one person
    for (int j = 0; j < n; j++) {
      BoolVar[] column = new BoolVar[n];
      for (int i = 0; i < n; i++) column[i] = x[i][j];
      m.sum(column, "=", 1).post();
    }

    // a person can only take a slot they are free in
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        if (free[i][j] == 0) {
          m.arithm(x[i][j], "=", 0).post();
        }
      }
    }

    out.put("x", x);
  }
}
