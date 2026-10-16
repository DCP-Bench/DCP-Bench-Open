import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Revenue maximisation: choose how many units of each package to sell so that the seats
// reserved on each flight leg do not exceed its capacity, and the total revenue is maximal.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] seats = inst.getIntArray("available_seats");     // seats[l]: capacity of leg l
    int[] demand = inst.getIntArray("demand");             // demand[p]: estimated demand for package p
    int[] revenue = inst.getIntArray("revenue");           // revenue[p]: price of package p
    int[][] delta = inst.getIntMatrix("delta");            // delta[p][l] = 1 if package p uses leg l
    int packages = demand.length;
    int legs = seats.length;

    // units of each package to sell, at most its demand
    IntVar[] sell = new IntVar[packages];
    for (int p = 0; p < packages; p++) sell[p] = m.intVar("sell" + p, 0, demand[p]);

    // seats reserved on each leg do not exceed the leg's capacity
    for (int l = 0; l < legs; l++) {
      int[] coeff = new int[packages];
      for (int p = 0; p < packages; p++) coeff[p] = delta[p][l];
      m.scalar(sell, coeff, "<=", seats[l]).post();
    }

    // total revenue is the sum of the price of each package times the units sold
    int maxRevenue = 0;
    for (int p = 0; p < packages; p++) maxRevenue += revenue[p] * demand[p];
    IntVar total = m.intVar("total", 0, maxRevenue, true);
    m.scalar(sell, revenue, "=", total).post();
    m.setObjective(Model.MAXIMIZE, total);

    out.put("packages_to_sell", sell);
    out.put("max_revenue", total);
  }
}
