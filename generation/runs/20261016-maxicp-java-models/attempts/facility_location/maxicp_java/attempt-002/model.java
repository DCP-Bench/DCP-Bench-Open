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

        // the warehouses that are opened (registered first, so they are branched on first)
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

        // a closed warehouse ships nothing to any region
        for (int i = 0; i < w; i++) {
            for (int j = 0; j < r; j++) {
                m.cp().post(le(ships[i][j], mul(open[i], Math.min(cap, demand[j]))));
            }
        }

        // an open warehouse ships at most max_shipping units in total, a closed one ships nothing
        for (int i = 0; i < w; i++) {
            CPIntVar capacity = mul(open[i], cap);
            CPIntVar[] outgoing = new CPIntVar[r];
            for (int j = 0; j < r; j++) outgoing[j] = ships[i][j];
            m.cp().post(ge(capacity, sum(outgoing)));
        }

        // implied: the open warehouses together have enough capacity for all the demand
        int totalDemand = 0;
        for (int d : demand) totalDemand += d;
        CPIntVar[] openCapacity = new CPIntVar[w];
        for (int i = 0; i < w; i++) openCapacity[i] = mul(open[i], cap);
        m.cp().post(ge(sum(openCapacity), totalDemand));

        // implied: each region's demand can be covered by the open warehouses
        for (int j = 0; j < r; j++) {
            CPIntVar[] reach = new CPIntVar[w];
            for (int i = 0; i < w; i++) reach[i] = mul(open[i], Math.min(cap, demand[j]));
            m.cp().post(ge(sum(reach), demand[j]));
        }

        // implied: a unit shipped into a region costs at least the cheapest open warehouse for that region.
        // cheapest[j] is that cheapest cost, tied to the open pattern by a table over every non-empty pattern
        CPIntVar[] cheapest = new CPIntVar[r];
        for (int j = 0; j < r; j++) {
            int lo = Integer.MAX_VALUE;
            int hi = 0;
            for (int i = 0; i < w; i++) {
                lo = Math.min(lo, shipCost[i][j]);
                hi = Math.max(hi, shipCost[i][j]);
            }
            cheapest[j] = m.intVar(lo, hi);
            int patterns = (1 << w) - 1;
            int[][] rows = new int[patterns][w + 1];
            for (int mask = 1; mask <= patterns; mask++) {
                int best = Integer.MAX_VALUE;
                for (int i = 0; i < w; i++) {
                    boolean isOpen = ((mask >> i) & 1) == 1;
                    rows[mask - 1][i] = isOpen ? 1 : 0;
                    if (isOpen) best = Math.min(best, shipCost[i][j]);
                }
                rows[mask - 1][w] = best;
            }
            CPIntVar[] cols = new CPIntVar[w + 1];
            for (int i = 0; i < w; i++) cols[i] = open[i];
            cols[w] = cheapest[j];
            m.cp().post(table(cols, rows));
        }

        // total cost: the fixed cost of each opened warehouse plus the shipping cost of every unit shipped
        CPIntVar[] costs = new CPIntVar[w + w * r];
        int k = 0;
        for (int i = 0; i < w; i++) {
            costs[k++] = mul(open[i], fixedCost[i]);
        }
        for (int i = 0; i < w; i++) {
            for (int j = 0; j < r; j++) costs[k++] = mul(ships[i][j], shipCost[i][j]);
        }

        // implied: the units shipped into region j cost at least demand[j] times its cheapest open warehouse
        for (int j = 0; j < r; j++) {
            CPIntVar[] regionCost = new CPIntVar[w];
            for (int i = 0; i < w; i++) regionCost[i] = mul(ships[i][j], shipCost[i][j]);
            m.cp().post(ge(sum(regionCost), mul(cheapest[j], demand[j])));
        }

        m.minimize(sum(costs));

        out.put("open_warehouse", open);
        out.put("ships", ships);
        out.put("total_cost", sum(costs));
    }
}
