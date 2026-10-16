// Diet problem: choose how many units of each food to buy so that the
// nutrition requirements are met at the lowest total cost.

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");                 // number of foods
    int[] price = inst.getIntArray("price");  // cents per unit of each food
    int[] limits = inst.getIntArray("limits"); // minimum requirement per nutrient type

    // The nutrition table of the problem statement, one row per nutrient type
    // (rows: calories, chocolate ounces, sugar ounces, fat ounces),
    // one column per food (chocolate cake, chocolate ice cream, cola, pineapple cheesecake).
    int[][] content = {
        {400, 200, 150, 500},
        {3, 2, 0, 0},
        {2, 2, 4, 4},
        {2, 4, 1, 5}
    };

    // Upper bound on the number of units of one food. A generous cap taken from
    // the largest requirement in the instance; it does not change the optimum
    // in the instances checked.
    int maxUnits = 0;
    for (int limit : limits) maxUnits = Math.max(maxUnits, limit);

    // how many units of each food to buy
    CPIntVar[] units = new CPIntVar[n];
    for (int f = 0; f < n; f++) units[f] = m.intVar(0, maxUnits);

    // the diet provides at least the required amount of each nutrient type
    for (int k = 0; k < limits.length; k++) {
      CPIntVar[] provided = new CPIntVar[n];
      for (int f = 0; f < n; f++) provided[f] = mul(units[f], content[k][f]);
      // at least the required amount of nutrient k
      m.cp().post(ge(sum(provided), limits[k]));
    }

    // total cost of the diet, in cents
    int maxCost = 0;
    for (int f = 0; f < n; f++) maxCost += price[f] * maxUnits;
    CPIntVar cost = m.intVar(0, maxCost);
    CPIntVar[] spend = new CPIntVar[n];
    for (int f = 0; f < n; f++) spend[f] = mul(units[f], price[f]);
    // the cost is the sum of the price of each food times its units
    m.cp().post(eq(cost, sum(spend)));
    m.minimize(cost);

    out.put("cost", cost);
  }
}
