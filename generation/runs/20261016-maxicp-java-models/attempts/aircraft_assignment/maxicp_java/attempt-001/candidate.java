import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Assign aircraft of several types to routes to minimize the total operational cost.
// Each aircraft type has a limited number of available units.
// Each route has a passenger demand that must be satisfied.
// allocation[i][j] is the number of aircraft of type i assigned to route j.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] availability = inst.getIntArray("availability");
    int[] demand = inst.getIntArray("demand");
    int[][] capabilities = inst.getIntMatrix("capabilities");
    int[][] costs = inst.getIntMatrix("costs");
    int types = availability.length;
    int routes = demand.length;

    // allocation[i][j] is the number of aircraft of type i assigned to route j
    CPIntVar[][] allocation = new CPIntVar[types][routes];
    for (int i = 0; i < types; i++)
      for (int j = 0; j < routes; j++)
        allocation[i][j] = m.intVar(0, availability[i]);

    // each aircraft type has a limited number of available units
    for (int i = 0; i < types; i++)
      m.cp().post(le(sum(allocation[i]), availability[i]));

    // each route has a passenger demand that must be satisfied by the passenger capacity of the aircraft assigned to it
    for (int j = 0; j < routes; j++) {
      CPIntVar[] seats = new CPIntVar[types];
      for (int i = 0; i < types; i++)
        seats[i] = mul(allocation[i][j], capabilities[i][j]);
      m.cp().post(ge(sum(seats), demand[j]));
    }

    // the overall operational cost is the sum over all aircraft assigned to all routes, to be minimized
    CPIntVar[] cost = new CPIntVar[types * routes];
    for (int i = 0; i < types; i++)
      for (int j = 0; j < routes; j++)
        cost[i * routes + j] = mul(allocation[i][j], costs[i][j]);
    m.minimize(sum(cost));

    out.put("allocation", allocation);
  }
}
