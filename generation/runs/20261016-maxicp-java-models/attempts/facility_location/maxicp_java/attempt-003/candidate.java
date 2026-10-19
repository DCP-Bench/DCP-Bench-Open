import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import java.util.Arrays;
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

        // implied: the units shipped into a region cost at least the cheapest way to cover its demand
        // from the open warehouses, each taking at most max_shipping units. regionCost[j] is that cost,
        // tied to the open pattern by a table over every non-empty pattern
        CPIntVar[] regionCost = new CPIntVar[r];
        for (int j = 0; j < r; j++) {
            int hiTotal = demand[j] * maxCostOf(shipCost, j, w);
            regionCost[j] = m.intVar(0, hiTotal);
            int patterns = (1 << w) - 1;
            int[][] rows = new int[patterns][w + 1];
            for (int mask = 1; mask <= patterns; mask++) {
                int[] openIdx = new int[w];
                int count = 0;
                for (int i = 0; i < w; i++) {
                    rows[mask - 1][i] = ((mask >> i) & 1);
                    if (((mask >> i) & 1) == 1) openIdx[count++] = i;
                }
                final int jj = j;
                Integer[] order = new Integer[count];
                for (int t = 0; t < count; t++) order[t] = openIdx[t];
                Arrays.sort(order, (a, b) -> shipCost[a][jj] - shipCost[b][jj]);
                int remaining = demand[j];
                int total = 0;
                for (int idx = 0; idx < count && remaining > 0; idx++) {
                    int i = order[idx];
                    int take = Math.min(Math.min(cap, demand[j]), remaining);
                    total += take * shipCost[i][j];
                    remaining -= take;
                }
                rows[mask - 1][w] = total;
            }
            CPIntVar[] cols = new CPIntVar[w + 1];
            for (int i = 0; i < w; i++) cols[i] = open[i];
            cols[w] = regionCost[j];
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

        // the shipping cost into each region is at least its cheapest open cover
        for (int j = 0; j < r; j++) {
            CPIntVar[] shipped = new CPIntVar[w];
            for (int i = 0; i < w; i++) shipped[i] = mul(ships[i][j], shipCost[i][j]);
            m.cp().post(ge(sum(shipped), regionCost[j]));
        }

        m.minimize(sum(costs));

        out.put("open_warehouse", open);
        out.put("ships", ships);
        out.put("total_cost", sum(costs));
    }

    private static int maxCostOf(int[][] shipCost, int j, int w) {
        int best = 0;
        for (int i = 0; i < w; i++) best = Math.max(best, shipCost[i][j]);
        return best;
    }
}
