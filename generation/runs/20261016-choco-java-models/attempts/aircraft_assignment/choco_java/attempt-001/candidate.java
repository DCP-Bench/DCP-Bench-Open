import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Aircraft assignment: assign aircraft of each type to each route so that every route's
// passenger demand is met, each type's available units are not exceeded, and the total
// operational cost is minimised. Output allocation[i][j] = number of type-i aircraft on route j.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] availability = inst.getIntArray("availability");  // units available per aircraft type
    int[] demand = inst.getIntArray("demand");              // passenger demand per route
    int[][] capabilities = inst.getIntMatrix("capabilities"); // passengers per aircraft of type i on route j
    int[][] costs = inst.getIntMatrix("costs");              // operational cost per aircraft of type i on route j

    int types = availability.length;
    int routes = demand.length;

    // allocation[i][j]: number of aircraft of type i assigned to route j, at most the units available
    IntVar[][] allocation = new IntVar[types][routes];
    for (int i = 0; i < types; i++) {
      for (int j = 0; j < routes; j++) {
        allocation[i][j] = m.intVar("alloc_" + i + "_" + j, 0, availability[i]);
      }
    }

    // each aircraft type has a limited number of available units
    for (int i = 0; i < types; i++) {
      m.sum(allocation[i], "<=", availability[i]).post();
    }

    // each route's passenger demand must be satisfied by the seats of the aircraft assigned to it
    for (int j = 0; j < routes; j++) {
      IntVar[] column = new IntVar[types];
      int[] seats = new int[types];
      for (int i = 0; i < types; i++) {
        column[i] = allocation[i][j];
        seats[i] = capabilities[i][j];
      }
      m.scalar(column, seats, ">=", demand[j]).post();
    }

    // total operational cost: the cost of every aircraft assigned, over all types and routes
    IntVar[] flat = new IntVar[types * routes];
    int[] flatCost = new int[types * routes];
    int maxCost = 0;
    for (int i = 0; i < types; i++) {
      for (int j = 0; j < routes; j++) {
        flat[i * routes + j] = allocation[i][j];
        flatCost[i * routes + j] = costs[i][j];
        maxCost += costs[i][j] * availability[i];  // upper bound: every unit of type i on the costliest route
      }
    }
    IntVar total = m.intVar("total_cost", 0, maxCost);
    m.scalar(flat, flatCost, "=", total).post();
    m.setObjective(Model.MINIMIZE, total);

    out.put("allocation", allocation);
  }
}
