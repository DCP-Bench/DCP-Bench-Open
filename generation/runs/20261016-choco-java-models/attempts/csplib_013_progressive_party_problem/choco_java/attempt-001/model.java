// Progressive party at a yacht club: choose the fewest host boats so that the crews of
// the other boats visit hosts in successive periods, within each host's capacity, with
// no two crews meeting more than once.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n_boats");          // number of boats
    int periods = inst.getInt("n_periods");  // number of half-hour periods
    int[] capacity = inst.getIntArray("capacity");   // people a boat can hold at a time
    int[] crew = inst.getIntArray("crew_size");      // crew size of each boat
    int totalCrew = 0;
    for (int c : crew) totalCrew += c;

    BoolVar[] isHost = m.boolVarArray("is_host", n);            // isHost[b]: boat b is a host
    IntVar[][] visits = m.intVarMatrix("visits", periods, n, 0, n - 1); // visits[p][b]: boat visited by b in period p

    // a host boat stays on board: in every period it is the boat it visits
    for (int p = 0; p < periods; p++) {
      for (int b = 0; b < n; b++) {
        isHost[b].eq(1).imp(visits[p][b].eq(b)).post();
      }
    }

    // every crew visits a host boat in every period
    for (int p = 0; p < periods; p++) {
      for (int b = 0; b < n; b++) {
        m.element(m.intVar(1), isHost, visits[p][b], 0).post();
      }
    }

    // the people aboard a host (its own crew plus the guest crews visiting it) do not exceed its capacity
    for (int p = 0; p < periods; p++) {
      for (int h = 0; h < n; h++) {
        IntVar[] present = new IntVar[n];
        int[] weight = new int[n];
        for (int g = 0; g < n; g++) {
          weight[g] = crew[g];
          // the host's own crew is aboard only when the boat is a host
          present[g] = (g == h) ? isHost[h] : m.isEq(visits[p][g], h);
        }
        IntVar load = m.intVar("load_" + p + "_" + h, 0, totalCrew);
        m.scalar(present, weight, "=", load).post();
        m.arithm(load, "<=", capacity[h]).post();
      }
    }

    // a guest crew cannot revisit a host, and two crews cannot meet more than once
    // (crews meet when they are aboard the same host in the same period)
    for (int i = 0; i < n; i++) {
      for (int j = i + 1; j < n; j++) {
        BoolVar[] meets = new BoolVar[periods];
        for (int p = 0; p < periods; p++) {
          meets[p] = m.boolVar();
          m.reifyXeqY(visits[p][i], visits[p][j], meets[p]);
        }
        m.sum(meets, "<=", 1).post();
      }
    }

    // minimise the number of host boats
    IntVar hosts = m.sum("hosts", isHost);
    m.setObjective(Model.MINIMIZE, hosts);

    out.put("is_host", isHost);
    out.put("visits", visits);
  }
}
