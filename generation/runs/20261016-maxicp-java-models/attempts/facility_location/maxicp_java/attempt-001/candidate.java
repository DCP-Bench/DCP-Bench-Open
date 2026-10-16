import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;

// Choose which warehouses to open and how many units each open warehouse ships to each region,
// so that every region gets its demand, each open warehouse ships at most max_shipping units,
// and the total of fixed opening costs and shipping costs is minimal.
public class Submission {
    public static void build(Instance inst, Model m, Outputs out) {
        int[] fixedCost = inst.getIntArray("fixed_costs");
        int[] demand = inst.getIntArray("demands");
        int[][] shipCost = inst.getIntMatrix("shipping_costs");
        int cap = inst.getInt("max_shipping");
        int w = fixedCost.length;   // warehouses, in the order of the description
        int r = demand.length;      // regions

        // the warehouses that are opened
        CPBoolVar[] open = m.boolVarArray(w);

        // the units shipped from each warehouse to each region, nothing beyond the demand of the region
        CPIntVar[][] ships = new CPIntVar[w][r];
        for (int i = 0; i < w; i++) {
            for (int j = 0; j < r; j++) {
                ships[i][j] = m.intVar(0, Math.min(cap, demand[j]));
            }
        }

        // no more than three warehouses are operational
        m.cp().post(le(sum(open), 3));

        // if the New York warehouse is opened, then the Los Angeles warehouse must also be opened
        m.cp().post(implies(open[0], open[1]));

        // either the Atlanta or the Los Angeles warehouse must be opened
        m.cp().post(or(new CPBoolVar[] {open[3], open[1]}));

        // each region receives exactly its demand
        for (int j = 0; j < r; j++) {
            CPIntVar[] incoming = new CPIntVar[w];
            for (int i = 0; i < w; i++) incoming[i] = ships[i][j];
            m.cp().post(eq(sum(incoming), demand[j]));
        }

        // an open warehouse ships at most max_shipping units in total, a closed one ships nothing
        for (int i = 0; i < w; i++) {
            CPIntVar capacity = mul(open[i], cap);
            CPIntVar[] outgoing = new CPIntVar[r];
            for (int j = 0; j < r; j++) outgoing[j] = ships[i][j];
            m.cp().post(ge(capacity, sum(outgoing)));
        }

        // total cost: the fixed cost of each opened warehouse plus the shipping cost of every unit shipped
        int upper = 0;
        for (int c : fixedCost) upper += c;
        for (int j = 0; j < r; j++) {
            int maxCost = 0;
            for (int i = 0; i < w; i++) maxCost = Math.max(maxCost, shipCost[i][j]);
            upper += demand[j] * maxCost;
        }
        CPIntVar[] costs = new CPIntVar[w * (r + 1)];
        int k = 0;
        for (int i = 0; i < w; i++) {
            costs[k++] = mul(open[i], fixedCost[i]);
            for (int j = 0; j < r; j++) costs[k++] = mul(ships[i][j], shipCost[i][j]);
        }
        CPIntVar total = m.intVar(0, upper);
        m.cp().post(eq(total, sum(costs)));
        m.minimize(total);

        out.put("open_warehouse", open);
        out.put("ships", ships);
        out.put("total_cost", total);
    }
}
