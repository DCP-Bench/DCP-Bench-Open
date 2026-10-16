import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Project assignment: person i works supply_i hours in total, project j gets demand_j hours
// in total, person i contributes at most limit_ij hours to project j, and the hours cost
// cost_ij per hour. Minimise the total cost.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] supply = inst.getIntArray("supply");
    int[] demand = inst.getIntArray("demand");
    int[][] cost = inst.getIntMatrix("cost");
    int[][] limit = inst.getIntMatrix("limit");
    int people = supply.length;
    int projects = demand.length;

    // hours assigned from each person to each project, between 0 and the person's limit on that project
    CPIntVar[][] assign = new CPIntVar[people][projects];
    int maxCost = 0;
    for (int i = 0; i < people; i++) {
      for (int j = 0; j < projects; j++) {
        assign[i][j] = m.intVar(0, limit[i][j]);
        maxCost += cost[i][j] * limit[i][j];
      }
    }

    // each person's hours over all projects equal that person's supply
    for (int i = 0; i < people; i++) {
      m.cp().post(eq(sum(assign[i]), supply[i]));
    }

    // each project's hours over all people equal that project's demand
    for (int j = 0; j < projects; j++) {
      CPIntVar[] column = new CPIntVar[people];
      for (int i = 0; i < people; i++) column[i] = assign[i][j];
      m.cp().post(eq(sum(column), demand[j]));
    }

    // the total cost is the sum of cost per hour times hours, over all person and project pairs
    CPIntVar[] terms = new CPIntVar[people * projects];
    int k = 0;
    for (int i = 0; i < people; i++) {
      for (int j = 0; j < projects; j++) {
        terms[k++] = mul(assign[i][j], cost[i][j]);
      }
    }
    CPIntVar total = m.intVar(0, maxCost);
    m.cp().post(eq(total, sum(terms)));
    m.minimize(total);

    out.put("assign", assign);
    out.put("total_cost", total);
  }
}
