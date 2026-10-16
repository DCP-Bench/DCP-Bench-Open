import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Resource-constrained project scheduling: give every job a start time so that each job
// starts after all its predecessors have finished, no resource is used above its capacity
// at any moment, and the project finishes as early as possible (minimise the makespan).
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] duration = inst.getIntArray("durations_data");
    int[][] need = inst.getIntMatrix("resource_needs_data");   // need[j][r]: units of resource r used by job j
    int[] capacity = inst.getIntArray("resource_capacities_data");
    int[][] links = inst.getIntMatrix("successors_link_data"); // [pred, succ]: pred must finish before succ starts
    int n = duration.length, resources = capacity.length;

    int horizon = 0;
    for (int d : duration) horizon += d;

    // start[j]: start time of job j
    IntVar[] start = m.intVarArray("start_time", n, 0, horizon, true);

    // a successor starts only after its predecessor has finished
    for (int[] link : links)
      m.arithm(start[link[1]], "-", start[link[0]], ">=", duration[link[0]]).post();

    // each resource is never used above its capacity at any moment
    for (int r = 0; r < resources; r++) {
      int[] use = new int[n];
      for (int j = 0; j < n; j++) use[j] = need[j][r];
      m.cumulative(start, duration, use, capacity[r]).post();
    }

    // the makespan: the latest finishing time of any job
    IntVar[] end = new IntVar[n];
    for (int j = 0; j < n; j++) end[j] = m.offset(start[j], duration[j]);
    IntVar makespan = m.intVar("makespan", 0, horizon, true);
    m.max(makespan, end).post();
    m.setObjective(Model.MINIMIZE, makespan);

    // schedule the earliest-starting jobs first, with restarts
    m.getSolver().setSearch(Search.inputOrderLBSearch(start));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("start_time", start);
  }
}
