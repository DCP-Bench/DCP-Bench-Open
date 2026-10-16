// Multi-commodity transportation: ship every product from the origins to the destinations so that
// the supplies are not exceeded, the demands are met, and the lane limits hold, at minimum total shipping cost.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] supply = inst.getIntMatrix("supply");   // supply[i][p]: supply of product p at origin i
    int[][] demand = inst.getIntMatrix("demand");   // demand[j][p]: demand of product p at destination j
    int[][] limit = inst.getIntMatrix("limit");     // limit[i][j]: total units on the lane from origin i to destination j
    int[][][] cost = inst.getInt3("cost");          // cost[i][j][p]: cost of one unit of product p from i to j
    int nO = supply.length;
    int nD = demand.length;
    int nP = supply[0].length;

    // ship[i][j][p]: units of product p shipped from origin i to destination j,
    // bounded by the smallest of the supply, the demand and the lane limit
    IntVar[][][] ship = new IntVar[nO][nD][nP];
    int maxCost = 0;
    for (int i = 0; i < nO; i++)
      for (int j = 0; j < nD; j++)
        for (int p = 0; p < nP; p++) {
          int ub = Math.min(supply[i][p], Math.min(demand[j][p], limit[i][j]));
          ship[i][j][p] = m.intVar("ship_" + i + "_" + j + "_" + p, 0, ub, false);
          maxCost += cost[i][j][p] * ub;
        }

    // origin i ships no more of product p than its supply of p
    for (int i = 0; i < nO; i++)
      for (int p = 0; p < nP; p++) {
        IntVar[] out_ip = new IntVar[nD];
        for (int j = 0; j < nD; j++) out_ip[j] = ship[i][j][p];
        m.sum(out_ip, "<=", supply[i][p]).post();
      }

    // destination j receives exactly its demand for product p
    for (int j = 0; j < nD; j++)
      for (int p = 0; p < nP; p++) {
        IntVar[] in_jp = new IntVar[nO];
        for (int i = 0; i < nO; i++) in_jp[i] = ship[i][j][p];
        m.sum(in_jp, "=", demand[j][p]).post();
      }

    // the lane from origin i to destination j carries at most its limit, over all products
    for (int i = 0; i < nO; i++)
      for (int j = 0; j < nD; j++) {
        IntVar[] lane = new IntVar[nP];
        for (int p = 0; p < nP; p++) lane[p] = ship[i][j][p];
        m.sum(lane, "<=", limit[i][j]).post();
      }

    // total cost: the shipping cost of each unit, summed over all shipments of all products
    int size = nO * nD * nP;
    IntVar[] flat = new IntVar[size];
    int[] coeffs = new int[size];
    int k = 0;
    for (int i = 0; i < nO; i++)
      for (int j = 0; j < nD; j++)
        for (int p = 0; p < nP; p++) {
          flat[k] = ship[i][j][p];
          coeffs[k] = cost[i][j][p];
          k++;
        }
    IntVar totalCost = m.intVar("total_cost", 0, maxCost, true);
    m.scalar(flat, coeffs, "=", totalCost).post();

    // minimise the total shipping cost of all products
    m.setObjective(Model.MINIMIZE, totalCost);

    out.put("total_cost", totalCost);
  }
}
