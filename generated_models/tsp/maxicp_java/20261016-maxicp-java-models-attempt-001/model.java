// Travelling salesman problem: visit each city exactly once and return to the
// origin city, minimising the total distance. Distances are Euclidean between
// the city locations, rounded to the nearest integer.

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] loc = inst.getIntMatrix("locations");
    int n = loc.length;

    // distance between every pair of cities, Euclidean rounded to an integer
    int[][] dist = new int[n][n];
    int maxDist = 0;
    for (int i = 0; i < n; i++) {
      for (int j = 0; j < n; j++) {
        double dx = loc[i][0] - loc[j][0];
        double dy = loc[i][1] - loc[j][1];
        dist[i][j] = (int) Math.round(Math.sqrt(dx * dx + dy * dy));
        maxDist = Math.max(maxDist, dist[i][j]);
      }
    }

    // the city visited after city i; the route is one cycle through all cities
    CPIntVar[] next = m.intVarArray(n, 0, n - 1);
    // every city is visited exactly once, and the successors form a single tour
    m.cp().post(allDifferent(next));
    m.cp().post(circuit(next));

    // the distance travelled from each city to the city after it
    CPIntVar[] legs = new CPIntVar[n];
    for (int i = 0; i < n; i++) {
      legs[i] = element(dist[i], next[i]);
    }

    // total travelled distance of the tour
    CPIntVar travel = m.intVar(0, n * maxDist);
    // the travel distance is the sum of the legs of the tour
    m.cp().post(eq(sum(legs), travel));
    // minimise the travel distance
    m.minimize(travel);

    out.put("travel_distance", travel);
  }
}
