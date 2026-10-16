// Car selection: assign participants to cars so that the number of assignments
// is maximal. Each participant may be interested in a subset of the cars. A
// participant is assigned to at most one car, and only to a car they are
// interested in. Each car is assigned to at most one participant.
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // interest of each participant in each car: 1 when participant i wants car j
    int[][] interested = inst.getIntMatrix("possible_assignments");
    int participants = interested.length;
    int cars = participants == 0 ? 0 : interested[0].length;

    // assignments[i][j] = 1 when participant i is assigned to car j
    CPBoolVar[][] assignments = new CPBoolVar[participants][cars];
    for (int i = 0; i < participants; i++) {
      for (int j = 0; j < cars; j++) {
        assignments[i][j] = m.boolVar();
        // a participant is assigned only to a car they are interested in
        if (interested[i][j] == 0) {
          m.cp().post(eq(assignments[i][j], 0));
        }
      }
    }

    // each participant is assigned to at most one car
    for (int i = 0; i < participants; i++) {
      m.cp().post(le(sum(assignments[i]), 1));
    }

    // each car is assigned to at most one participant
    for (int j = 0; j < cars; j++) {
      CPIntVar[] column = new CPIntVar[participants];
      for (int i = 0; i < participants; i++) {
        column[i] = assignments[i][j];
      }
      m.cp().post(le(sum(column), 1));
    }

    // maximize the total number of assignments
    CPIntVar[] all = new CPIntVar[participants * cars];
    for (int i = 0; i < participants; i++) {
      for (int j = 0; j < cars; j++) {
        all[i * cars + j] = assignments[i][j];
      }
    }
    m.maximize(sum(all));

    out.put("assignments", assignments);
  }
}
