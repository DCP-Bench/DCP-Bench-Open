// Project assignment (a transportation problem): decide how many hours each person
// i works on each project j, so that every person's supply and every project's
// demand is met exactly, each pair stays within its limit, and the total cost is minimal.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] supply = inst.getIntArray("supply");   // Supply_i: available hours of person i
    int[] demand = inst.getIntArray("demand");   // Demand_j: hours required by project j
    int[][] cost = inst.getIntMatrix("cost");    // Cost_ij: cost per hour of person i on project j
    int[][] limit = inst.getIntMatrix("limit");  // Limit_ij: maximum hours of person i on project j
    int people = supply.length;
    int projects = demand.length;

    // assign[i][j]: hours from person i to project j, bounded by the limit
    IntVar[][] assign = new IntVar[people][projects];
    for (int i = 0; i < people; i++) {
      for (int j = 0; j < projects; j++) {
        assign[i][j] = m.intVar("assign_" + i + "_" + j, 0, limit[i][j]);
      }
    }

    // the total hours assigned from each person equals its supply
    for (int i = 0; i < people; i++) {
      m.sum(assign[i], "=", supply[i]).post();
    }

    // the total hours assigned to each project equals its demand
    for (int j = 0; j < projects; j++) {
      IntVar[] column = new IntVar[people];
      for (int i = 0; i < people; i++) column[i] = assign[i][j];
      m.sum(column, "=", demand[j]).post();
    }

    // total cost: sum of Cost_ij times the hours assigned from i to j
    int maxCost = 0;
    IntVar[] flat = new IntVar[people * projects];
    int[] coeffs = new int[people * projects];
    int k = 0;
    for (int i = 0; i < people; i++) {
      for (int j = 0; j < projects; j++) {
        flat[k] = assign[i][j];
        coeffs[k] = cost[i][j];
        maxCost += cost[i][j] * limit[i][j];
        k++;
      }
    }
    IntVar total = m.intVar("total_cost", 0, maxCost, true);
    m.scalar(flat, coeffs, "=", total).post();
    m.setObjective(Model.MINIMIZE, total);

    out.put("assign", assign);
    out.put("total_cost", total);
  }
}
