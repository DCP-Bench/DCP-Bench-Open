// Multi-commodity transportation: ship every product from the origins to the
// destinations so that the total shipping cost is minimal.
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int[][] supply = inst.getIntMatrix("supply");  // supply[i][p]: units of product p at origin i
    int[][] demand = inst.getIntMatrix("demand");  // demand[j][p]: units of product p wanted at destination j
    int[][] limit = inst.getIntMatrix("limit");    // limit[i][j]: total units on the lane from origin i to destination j
    int[][][] cost = inst.getInt3("cost");         // cost[i][j][p]: cost of one unit of product p from i to j
    int nO = supply.length;
    int nD = demand.length;
    int nP = supply[0].length;

    // x[i][j][p] = units of product p shipped from origin i to destination j.
    // Upper bound: no more than the origin can send, the destination can take,
    // or the lane can carry, all read from the instance.
    CPIntVar[][][] x = new CPIntVar[nO][nD][nP];
    for (int i = 0; i < nO; i++)
      for (int j = 0; j < nD; j++)
        for (int p = 0; p < nP; p++) {
          int ub = Math.min(supply[i][p], Math.min(demand[j][p], limit[i][j]));
          x[i][j][p] = m.intVar(0, ub);
        }

    // origin i ships out no more than its supply of product p
    for (int i = 0; i < nO; i++)
      for (int p = 0; p < nP; p++) {
        CPIntVar[] out_ip = new CPIntVar[nD];
        for (int j = 0; j < nD; j++) out_ip[j] = x[i][j][p];
        m.cp().post(le(sum(out_ip), supply[i][p]));
      }

    // every destination j receives exactly its demand of product p
    for (int j = 0; j < nD; j++)
      for (int p = 0; p < nP; p++) {
        CPIntVar[] in_jp = new CPIntVar[nO];
        for (int i = 0; i < nO; i++) in_jp[i] = x[i][j][p];
        m.cp().post(sum(in_jp, demand[j][p]));
      }

    // the lane from origin i to destination j carries at most limit[i][j] units,
    // summed over all products
    for (int i = 0; i < nO; i++)
      for (int j = 0; j < nD; j++) {
        CPIntVar[] lane = new CPIntVar[nP];
        for (int p = 0; p < nP; p++) lane[p] = x[i][j][p];
        m.cp().post(le(sum(lane), limit[i][j]));
      }

    // total_cost: the shipping cost of all products, sum of cost[i][j][p] * x[i][j][p].
    // The objective is a plain variable bounded by the largest possible cost, fixed by eq.
    int maxCost = 0;
    CPIntVar[] terms = new CPIntVar[nO * nD * nP];
    int k = 0;
    for (int i = 0; i < nO; i++)
      for (int j = 0; j < nD; j++)
        for (int p = 0; p < nP; p++) {
          terms[k++] = mul(x[i][j][p], cost[i][j][p]);
          maxCost += cost[i][j][p] * x[i][j][p].max();
        }
    CPIntVar total = m.intVar(0, maxCost);
    m.cp().post(eq(total, sum(terms)));
    m.minimize(total);
    out.put("total_cost", total);
  }
}
