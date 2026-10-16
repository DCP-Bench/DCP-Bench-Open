import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Travelling salesman: a shortest tour that visits every city exactly once and
// returns to the start, with distances rounded to the nearest integer.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] locations = inst.getIntMatrix("locations");
    int n = locations.length;

    // dist[i][j]: Euclidean distance between cities i and j, rounded to an integer.
    // Computed from the instance coordinates, not typed in.
    int[][] dist = new int[n][n];
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        double dx = locations[i][0] - locations[j][0];
        double dy = locations[i][1] - locations[j][1];
        dist[i][j] = (int) Math.round(Math.sqrt(dx * dx + dy * dy));
      }
    }

    // succ[i]: the city visited right after city i (0-based)
    IntVar[] succ = m.intVarArray("succ", n, 0, n - 1);

    // the route visits every city exactly once and returns to the origin (one cycle, no sub-tours)
    m.circuit(succ).post();

    // cost[i]: distance travelled from city i to the next city on the route
    IntVar[] cost = new IntVar[n];
    for (int i = 0; i < n; i++) {
      int lo = Integer.MAX_VALUE, hi = 0;
      for (int j = 0; j < n; j++) {
        if (j == i) continue;
        lo = Math.min(lo, dist[i][j]);
        hi = Math.max(hi, dist[i][j]);
      }
      cost[i] = m.intVar("cost_" + i, lo, hi);
      m.element(cost[i], dist[i], succ[i]).post();
    }

    // the optimal travel distance: the total length of the route
    IntVar total = m.sum("travel_distance", cost);
    m.setObjective(Model.MINIMIZE, total);

    // branch on the successors, the most constrained city first
    Solver solver = m.getSolver();
    solver.setSearch(Search.minDomLBSearch(succ));

    out.put("travel_distance", total);
  }
}
