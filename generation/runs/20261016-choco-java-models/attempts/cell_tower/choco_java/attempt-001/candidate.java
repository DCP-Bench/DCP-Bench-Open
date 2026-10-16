import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Choose which potential cell tower sites to build, within the budget, so that the
// population covered by the towers is as large as possible. A region is covered when
// at least one built site reaches it.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] delta = inst.getIntMatrix("delta");   // delta[s][r] = 1 if site s covers region r
    int[] cost = inst.getIntArray("cost");        // cost of building a tower at each site
    int[] population = inst.getIntArray("population"); // population of each region
    int budget = inst.getInt("budget");

    int sites = cost.length;
    int regions = population.length;

    // build[s] = 1 if a tower is built at site s
    BoolVar[] build = m.boolVarArray("build", sites);

    // only a limited number of towers can be built: their total cost stays within the budget
    m.scalar(build, cost, "<=", budget).post();

    // covered[r] = 1 if region r is reached by a built tower
    BoolVar[] covered = m.boolVarArray("covered", regions);
    for (int r = 0; r < regions; r++) {
      int coveringSites = 0;
      for (int s = 0; s < sites; s++) if (delta[s][r] == 1) coveringSites++;
      if (coveringSites == 0) {
        // no site reaches this region, so it can not be covered
        covered[r].eq(0).post();
        continue;
      }
      IntVar[] reaching = new IntVar[coveringSites];
      int k = 0;
      for (int s = 0; s < sites; s++) {
        if (delta[s][r] == 1) {
          reaching[k++] = build[s];
          // a built site covering the region means the region is covered
          build[s].le(covered[r]).post();
        }
      }
      // a covered region needs at least one built site that reaches it
      m.sum(reaching, ">=", covered[r]).post();
    }

    // total population covered by the built towers
    int totalPopulation = 0;
    for (int p : population) totalPopulation += p;
    IntVar total = m.intVar("total_population_covered", 0, totalPopulation);
    m.scalar(covered, population, "=", total).post();
    m.setObjective(Model.MAXIMIZE, total);

    out.put("build_tower", build);
    out.put("total_population_covered", total);
  }
}
