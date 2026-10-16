// Diet problem: choose how many units of each of four foods to buy, so that the nutritional
// requirements (at least) are met at the lowest total cost.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[] price = inst.getIntArray("price");     // price of one unit of each food, in cents
    int[] limits = inst.getIntArray("limits");   // minimum calories, chocolate, sugar, fat

    // nutrient content per unit of each food (fixed by the problem's food table):
    // Chocolate Cake, Chocolate ice cream, Cola, Pineapple cheesecake
    int[] calories = {400, 200, 150, 500};
    int[] chocolate = {3, 2, 0, 0};
    int[] sugar = {2, 2, 4, 4};
    int[] fat = {2, 4, 1, 5};
    int[][] content = {calories, chocolate, sugar, fat};

    int n = price.length;
    // number of units of each food; the upper bound is generous (no food needs more
    // units than the sum of all requirements)
    int ub = 0;
    for (int limit : limits) ub += limit;
    IntVar[] units = m.intVarArray("units", n, 0, ub, true);

    // each nutrient requirement is met at least
    for (int k = 0; k < limits.length; k++) {
      m.scalar(units, content[k], ">=", limits[k]).post();
    }

    // total cost of the diet
    int maxCost = 0;
    for (int p : price) maxCost += p * ub;
    IntVar cost = m.intVar("cost", 0, maxCost, true);
    m.scalar(units, price, "=", cost).post();
    m.setObjective(Model.MINIMIZE, cost);

    out.put("cost", cost);
  }
}
