import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Facility location: choose which warehouses to open and how much each open warehouse ships
// to each region, so that every regional demand is met, at minimal total fixed and shipping cost.
public class Submission {

  // position of a city in the instance's warehouse list
  static int cityIndex(String[] cities, String city) {
    for (int i = 0; i < cities.length; i++) if (cities[i].equals(city)) return i;
    throw new IllegalArgumentException("warehouse " + city + " is not in warehouse_s");
  }

  public static void build(Instance inst, Model m, Outputs out) {
    String[] cities = inst.getStringArray("warehouse_s");
    int[] fixedCost = inst.getIntArray("fixed_costs");
    int[] demands = inst.getIntArray("demands");
    int[][] shippingCost = inst.getIntMatrix("shipping_costs");
    int capacity = inst.getInt("max_shipping");
    int W = cities.length;   // candidate warehouses
    int R = demands.length;  // regions
    int NY = cityIndex(cities, "New York");
    int LA = cityIndex(cities, "Los Angeles");
    int ATL = cityIndex(cities, "Atlanta");

    // open[i] = 1 if warehouse i is opened
    BoolVar[] open = m.boolVarArray("open", W);
    // ships[i][j]: units shipped from warehouse i to region j, never more than the region's demand
    IntVar[][] ships = new IntVar[W][R];
    for (int i = 0; i < W; i++)
      for (int j = 0; j < R; j++)
        ships[i][j] = m.intVar("ships_" + i + "_" + j, 0, demands[j]);

    // every region's demand is met by the shipments into it
    for (int j = 0; j < R; j++) {
      IntVar[] into = new IntVar[W];
      for (int i = 0; i < W; i++) into[i] = ships[i][j];
      m.sum(into, "=", demands[j]).post();
    }

    // a warehouse ships at most max_shipping, and nothing when it is closed
    for (int i = 0; i < W; i++) {
      IntVar[] vars = new IntVar[R + 1];
      int[] coeffs = new int[R + 1];
      for (int j = 0; j < R; j++) { vars[j] = ships[i][j]; coeffs[j] = 1; }
      vars[R] = open[i];
      coeffs[R] = -capacity;
      m.scalar(vars, coeffs, "<=", 0).post();
    }

    // restriction 1: if the New York warehouse is opened, the Los Angeles one must also be opened
    m.arithm(open[NY], "<=", open[LA]).post();

    // restriction 2: no more than three warehouses can be operational
    m.sum(open, "<=", 3).post();

    // restriction 3: either the Atlanta or the Los Angeles warehouse must be opened
    m.sum(new IntVar[]{open[ATL], open[LA]}, ">=", 1).post();

    // total cost = fixed costs of the open warehouses + shipping cost of every shipment
    int upper = 0;
    for (int i = 0; i < W; i++) {
      upper += fixedCost[i];
      for (int j = 0; j < R; j++) upper += shippingCost[i][j] * demands[j];
    }
    IntVar total = m.intVar("total_cost", 0, upper, true);
    IntVar[] costVars = new IntVar[W + W * R + 1];
    int[] costCoeffs = new int[W + W * R + 1];
    int k = 0;
    for (int i = 0; i < W; i++) { costVars[k] = open[i]; costCoeffs[k++] = fixedCost[i]; }
    for (int i = 0; i < W; i++)
      for (int j = 0; j < R; j++) { costVars[k] = ships[i][j]; costCoeffs[k++] = shippingCost[i][j]; }
    costVars[k] = total; costCoeffs[k] = -1;
    m.scalar(costVars, costCoeffs, "=", 0).post();
    m.setObjective(Model.MINIMIZE, total);

    out.put("open_warehouse", open);
    out.put("ships", ships);
    out.put("total_cost", total);
  }
}
