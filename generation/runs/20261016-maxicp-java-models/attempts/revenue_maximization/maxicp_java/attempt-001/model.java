// Revenue maximization: choose how many units of each itinerary package to sell.
// Each flight leg has a limited number of seats; a package uses the legs in its
// delta row, and each unit sold reserves one seat on each of those legs.
// Maximise the total revenue of the packages sold.

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

import java.util.ArrayList;
import java.util.List;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // the packages, the legs, and the data of each, from the instance
    int[] demand = inst.getIntArray("demand");           // estimated demand of each package
    int[] revenue = inst.getIntArray("revenue");         // price of one unit of each package
    int[] seats = inst.getIntArray("available_seats");   // passenger seats available on each leg
    int[][] delta = inst.getIntMatrix("delta");          // delta[p][l] = 1 if package p uses leg l
    int packages = demand.length;
    int legs = seats.length;

    // units of each package to sell, between 0 and its estimated demand
    CPIntVar[] sell = new CPIntVar[packages];
    for (int p = 0; p < packages; p++) {
      sell[p] = m.intVar(0, demand[p]);
    }

    // the seats reserved on each leg by the packages sold over it do not exceed its seats
    for (int l = 0; l < legs; l++) {
      List<CPIntVar> onLeg = new ArrayList<>();
      for (int p = 0; p < packages; p++) {
        if (delta[p][l] == 1) onLeg.add(sell[p]);
      }
      if (!onLeg.isEmpty()) {
        m.cp().post(le(sum(onLeg.toArray(new CPIntVar[0])), seats[l]));
      }
    }

    // the total revenue is the sum of the units sold times the price of each package
    CPIntVar[] earned = new CPIntVar[packages];
    int maxTotal = 0;
    for (int p = 0; p < packages; p++) {
      earned[p] = mul(sell[p], revenue[p]);
      maxTotal += revenue[p] * demand[p];
    }
    CPIntVar total = m.intVar(0, maxTotal);
    m.cp().post(eq(total, sum(earned)));

    // maximise the total revenue
    m.maximize(total);

    out.put("max_revenue", total);
    out.put("packages_to_sell", sell);
  }
}
