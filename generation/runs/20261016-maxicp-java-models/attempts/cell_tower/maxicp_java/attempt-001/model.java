import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Cell towers: choose which candidate sites to build towers on, so that the population
// covered by the towers is as large as possible, within a budget on the total cost.
// A region is covered when at least one built tower reaches it.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] delta = inst.getIntMatrix("delta");
    int[] cost = inst.getIntArray("cost");
    int[] population = inst.getIntArray("population");
    int budget = inst.getInt("budget");
    int sites = cost.length;
    int regions = population.length;

    // build_tower[s] = 1 if a tower is built on site s
    CPBoolVar[] build = m.boolVarArray(sites);

    // covered[r] = 1 if region r is reached by some built tower
    CPBoolVar[] covered = new CPBoolVar[regions];
    for (int r = 0; r < regions; r++) covered[r] = m.boolVar();

    // the total cost of the towers built must stay within the budget
    CPIntVar[] costs = new CPIntVar[sites];
    for (int s = 0; s < sites; s++) costs[s] = mul(build[s], cost[s]);
    m.cp().post(le(sum(costs), budget));

    // a region is covered only if at least one tower built on a site that reaches it
    for (int r = 0; r < regions; r++) {
      int covering = 0;
      for (int s = 0; s < sites; s++) if (delta[s][r] == 1) covering++;
      if (covering == 0) {
        // no candidate site reaches this region, so it stays uncovered
        m.cp().post(eq(covered[r], 0));
        continue;
      }
      CPIntVar[] reaching = new CPIntVar[covering];
      int k = 0;
      for (int s = 0; s < sites; s++) if (delta[s][r] == 1) reaching[k++] = build[s];
      m.cp().post(ge(sum(reaching), covered[r]));
    }

    // the population covered by the towers built
    CPIntVar[] covered_population = new CPIntVar[regions];
    for (int r = 0; r < regions; r++) covered_population[r] = mul(covered[r], population[r]);
    CPIntVar total = sum(covered_population);

    // maximise the total population covered
    m.maximize(total);

    out.put("build_tower", build);
    out.put("total_population_covered", total);
  }
}
