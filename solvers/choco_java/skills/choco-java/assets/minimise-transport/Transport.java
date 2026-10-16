// Ship goods from 2 warehouses to 3 shops at minimum total cost. Warehouse supplies
// are 20 and 30; shop demands are 10, 25 and 15; the cost of one unit from warehouse
// w to shop s is COST[w][s]. Shows: a grid of integer flows, sum for supply and demand
// limits, scalar for the total cost, minimisation with setObjective.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.SearchState;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;

public class Transport {
    static final int[] SUPPLY = {20, 30};
    static final int[] DEMAND = {10, 25, 15};
    static final int[][] COST = {{4, 6, 9}, {5, 3, 7}};

    public static void main(String[] args) {
        int warehouses = SUPPLY.length, shops = DEMAND.length;
        Model m = new Model("transport");
        IntVar[][] flow = m.intVarMatrix("flow", warehouses, shops, 0, 50);

        // a warehouse ships out no more than it holds
        for (int w = 0; w < warehouses; w++) m.sum(flow[w], "<=", SUPPLY[w]).post();

        // each shop receives exactly what it needs
        for (int s = 0; s < shops; s++) {
            IntVar[] incoming = new IntVar[warehouses];
            for (int w = 0; w < warehouses; w++) incoming[w] = flow[w][s];
            m.sum(incoming, "=", DEMAND[s]).post();
        }

        // total cost: every unit shipped pays its route's cost
        IntVar[] all = new IntVar[warehouses * shops];
        int[] price = new int[warehouses * shops];
        for (int w = 0; w < warehouses; w++)
            for (int s = 0; s < shops; s++) {
                all[w * shops + s] = flow[w][s];
                price[w * shops + s] = COST[w][s];
            }
        IntVar total = m.intVar("total", 0, 10000, true);
        m.scalar(all, price, "=", total).post();
        m.setObjective(Model.MINIMIZE, total);
        m.getSolver().setSearch(Search.inputOrderLBSearch(all));

        // every solution found is better than the one before; keep the values of the last
        int[][] best = null;
        int bestCost = -1;
        while (m.getSolver().solve()) {
            bestCost = total.getValue();
            best = new int[warehouses][shops];
            for (int w = 0; w < warehouses; w++)
                for (int s = 0; s < shops; s++) best[w][s] = flow[w][s].getValue();
        }
        if (best != null && m.getSolver().getSearchState() == SearchState.TERMINATED) {
            System.out.println("Minimum cost: " + bestCost);
            for (int w = 0; w < warehouses; w++) {
                StringBuilder row = new StringBuilder("warehouse " + w + ":");
                for (int s = 0; s < shops; s++) row.append(' ').append(best[w][s]);
                System.out.println(row);
            }
        } else {
            System.out.println("no proven optimum");
        }
    }
}
