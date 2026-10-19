// Appointment scheduling: assign people to interview slots based on their
// free-busy schedules. m[i][j] = 1 means person i is free in slot j.
// x[i][j] = 1 means person i is assigned to slot j.

import org.maxicp.cp.engine.core.CPBoolVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] free = inst.getIntMatrix("m");
    int people = free.length;
    int slots = free[0].length;

    // x[i][j] = 1 if person i is assigned to slot j
    CPBoolVar[][] x = new CPBoolVar[people][slots];
    for (int i = 0; i < people; i++)
      for (int j = 0; j < slots; j++)
        x[i][j] = m.boolVar();

    // a person can only be placed in a slot when they are free in it
    for (int i = 0; i < people; i++)
      for (int j = 0; j < slots; j++)
        if (free[i][j] == 0)
          m.cp().post(eq(x[i][j], 0));

    // each person is assigned to exactly one slot
    for (int i = 0; i < people; i++)
      m.cp().post(eq(sum(x[i]), 1));

    // each slot holds at most one person
    for (int j = 0; j < slots; j++) {
      CPBoolVar[] column = new CPBoolVar[people];
      for (int i = 0; i < people; i++)
        column[i] = x[i][j];
      m.cp().post(le(sum(column), 1));
    }

    out.put("x", x);
  }
}
