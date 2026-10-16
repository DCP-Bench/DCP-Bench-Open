import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// A company manufactures shirts, shorts and pants. Each product needs labor
// hours and cloth, the company has limited capacity of both, and every product
// can only be manufactured by renting its machine. Maximise the profit
// (products sold minus the machine rents).
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    var cp = m.cp();
    int numProducts = inst.getInt("num_products");
    int numMachines = inst.getInt("num_machines");
    int[] productIds = inst.getIntArray("products");
    int[][] product = inst.getIntMatrix("product"); // product[p][0] is the profit per unit
    int[][] use = inst.getIntMatrix("use");         // use[p][r] is the amount of resource r per unit of p
    int[] capacity = inst.getIntArray("capacity");
    int[] rentingCost = inst.getIntArray("renting_cost");
    int maxProduction = inst.getInt("max_production");
    int shirt = inst.getInt("shirt");
    int shorts = inst.getInt("shorts");
    int pants = inst.getInt("pants");
    int shirtM = inst.getInt("shirtM");
    int shortM = inst.getInt("shortM");
    int pantM = inst.getInt("pantM");

    // the machine each product is made on
    int[] machineOf = new int[numProducts];
    for (int p = 0; p < numProducts; p++) {
      int id = productIds[p];
      machineOf[p] = id == shirt ? shirtM : id == shorts ? shortM : pantM;
    }

    // how many units of each product are made, at most the maximum production
    CPIntVar[] made = new CPIntVar[numProducts];
    for (int p = 0; p < numProducts; p++) made[p] = m.intVar(0, maxProduction);

    // a machine is rented or not
    CPBoolVar[] rented = m.boolVarArray(numMachines);

    // a product is made only if its machine is rented
    for (int p = 0; p < numProducts; p++) {
      // a machine must be rented to manufacture anything on it
      cp.post(le(made[p], mul(rented[machineOf[p]], maxProduction)));
    }

    // the company has limited capacity of each resource (labor and cloth)
    for (int r = 0; r < capacity.length; r++) {
      CPIntVar[] usage = new CPIntVar[numProducts];
      for (int p = 0; p < numProducts; p++) usage[p] = mul(made[p], use[p][r]);
      // the resource used by all products stays within its capacity
      cp.post(le(sum(usage), capacity[r]));
    }

    // the profit is the sales of the products minus the rent of the machines
    int lo = 0;
    int hi = 0;
    for (int p = 0; p < numProducts; p++) {
      int sales = product[p][0] * maxProduction;
      lo += Math.min(0, sales);
      hi += Math.max(0, sales);
    }
    for (int mc = 0; mc < numMachines; mc++) lo -= rentingCost[mc];

    CPIntVar profit = m.intVar(lo, hi);
    CPIntVar[] terms = new CPIntVar[numProducts + numMachines];
    for (int p = 0; p < numProducts; p++) terms[p] = mul(made[p], product[p][0]);
    // the rent of each machine is paid only when it is rented
    for (int mc = 0; mc < numMachines; mc++) terms[numProducts + mc] = minus(mul(rented[mc], rentingCost[mc]));
    // the profit equals the sales minus the rents
    cp.post(eq(profit, sum(terms)));

    m.maximize(profit);
    out.put("z", profit);
  }
}
