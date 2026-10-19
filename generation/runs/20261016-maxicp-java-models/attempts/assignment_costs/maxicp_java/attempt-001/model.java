// Assignment costs: assign people to 4 tasks with different costs, so that the total cost is minimized.
// cost[i][j] is the cost of assigning task i to person j.

import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] cost = inst.getIntMatrix("cost");
    int tasks = cost.length;
    int people = cost[0].length;

    // x[i][j] is True if task i is assigned to person j.
    CPBoolVar[][] x = new CPBoolVar[tasks][people];
    for (int i = 0; i < tasks; i++) {
      for (int j = 0; j < people; j++) {
        x[i][j] = m.boolVar();
      }
    }

    // Each task must be assigned to exactly one person.
    for (int i = 0; i < tasks; i++) {
      m.cp().post(eq(sum(x[i]), 1));
    }

    // Not necessary to assign all people to a task: each person takes at most one task.
    for (int j = 0; j < people; j++) {
      CPIntVar[] column = new CPIntVar[tasks];
      for (int i = 0; i < tasks; i++) {
        column[i] = x[i][j];
      }
      m.cp().post(le(sum(column), 1));
    }

    // Assign people to tasks so that the total cost is minimized.
    CPIntVar[] terms = new CPIntVar[tasks * people];
    int k = 0;
    for (int i = 0; i < tasks; i++) {
      for (int j = 0; j < people; j++) {
        terms[k++] = mul(x[i][j], cost[i][j]);
      }
    }
    m.minimize(sum(terms));

    out.put("x", x);
  }
}
