// Assignment with costs: assign each of the tasks to exactly one person, each person takes
// at most one task, and the total cost is minimised. x[i][j] = 1 means task i goes to person j.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] cost = inst.getIntMatrix("cost");   // cost[i][j]: cost of task i done by person j
    int tasks = cost.length;
    int people = cost[0].length;

    BoolVar[][] x = m.boolVarMatrix("x", tasks, people);

    // each task is assigned to exactly one person
    for (int i = 0; i < tasks; i++) {
      m.sum(x[i], "=", 1).post();
    }

    // not every person needs a task, but each person takes at most one
    for (int j = 0; j < people; j++) {
      BoolVar[] column = new BoolVar[tasks];
      for (int i = 0; i < tasks; i++) column[i] = x[i][j];
      m.sum(column, "<=", 1).post();
    }

    // total cost: the sum of cost[i][j] over the chosen assignments
    IntVar[] chosen = new IntVar[tasks * people];
    int[] weight = new int[tasks * people];
    int upper = 0;
    for (int i = 0; i < tasks; i++) {
      int rowMax = 0;
      for (int j = 0; j < people; j++) {
        chosen[i * people + j] = x[i][j];
        weight[i * people + j] = cost[i][j];
        rowMax = Math.max(rowMax, cost[i][j]);
      }
      upper += rowMax;   // an upper bound on the cost of any assignment
    }
    IntVar total = m.intVar("total", 0, upper, true);
    m.scalar(chosen, weight, "=", total).post();
    m.setObjective(Model.MINIMIZE, total);

    out.put("x", x);
  }
}
