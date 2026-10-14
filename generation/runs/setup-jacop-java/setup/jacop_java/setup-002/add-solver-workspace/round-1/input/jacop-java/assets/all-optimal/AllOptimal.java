// Assign each task to a different worker, maximising total profit, then print
// every optimal assignment. Shows: Alldifferent, Element with a 0-based offset,
// maximising through a negated cost, the proof check, and enumerating the
// optimal solutions on a fresh store with the objective fixed.
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

import org.jacop.constraints.Alldifferent;
import org.jacop.constraints.Element;
import org.jacop.constraints.SumInt;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XmulCeqZ;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.DepthFirstSearch;
import org.jacop.search.IndomainMin;
import org.jacop.search.SimpleSelect;
import org.json.JSONArray;
import org.json.JSONObject;

public class AllOptimal {
    static int[][] profit;

    /** Variables of one model instance; built afresh for each solve. */
    record Built(Store store, IntVar[] worker, IntVar total) {}

    static Built build() {
        int workers = profit.length, tasks = profit[0].length;
        Store store = new Store();
        IntVar[] worker = new IntVar[tasks];
        IntVar[] gain = new IntVar[tasks];
        for (int t = 0; t < tasks; t++) {
            worker[t] = new IntVar(store, "worker" + t, 0, workers - 1);
            int[] column = new int[workers];
            for (int w = 0; w < workers; w++) column[w] = profit[w][t];
            gain[t] = new IntVar(store, "gain" + t, 0, Arrays.stream(column).max().getAsInt());
            // Element is 1-based by default; offset -1 makes worker[t] a 0-based index.
            store.impose(Element.choose(worker[t], column, gain[t], -1));
        }
        store.impose(new Alldifferent(worker));
        IntVar total = new IntVar(store, "total", 0, 1000);
        store.impose(new SumInt(gain, "==", total));
        return new Built(store, worker, total);
    }

    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args.length > 0 ? args[0] : "data.json")));
        JSONArray rows = data.getJSONArray("profit");
        profit = new int[rows.length()][];
        for (int r = 0; r < rows.length(); r++) {
            JSONArray row = rows.getJSONArray(r);
            profit[r] = new int[row.length()];
            for (int c = 0; c < row.length(); c++) profit[r][c] = row.getInt(c);
        }

        // 1. Maximise: JaCoP minimises its cost variable, so minimise -total.
        Built m = build();
        IntVar negated = new IntVar(m.store(), "negated", -1000, 0);
        m.store().impose(new XmulCeqZ(m.total(), -1, negated));
        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setTimeOut(10);  // seconds
        boolean found = search.labeling(m.store(),
                new SimpleSelect<>(m.worker(), null, new IndomainMin<>()), negated);
        if (!found) {
            System.out.println(search.timeOutOccured ? "timeout, nothing found" : "infeasible");
            return;
        }
        if (search.timeOutOccured) {
            System.out.println("timeout: best found " + m.total().value() + " is not proven optimal");
            return;
        }
        int best = m.total().value();
        System.out.println("Optimum: " + best);

        // 2. Enumerate on a fresh store with the objective fixed.
        Built e = build();
        e.store().impose(new XeqC(e.total(), best));
        DepthFirstSearch<IntVar> all = new DepthFirstSearch<>();
        all.setPrintInfo(false);
        all.getSolutionListener().searchAll(true);
        all.getSolutionListener().recordSolutions(true);
        all.labeling(e.store(), new SimpleSelect<>(e.worker(), null, new IndomainMin<>()));
        // The search variables are exactly the outputs, so solutions are distinct.
        for (int i = 1; i <= all.getSolutionListener().solutionsNo(); i++) {
            System.out.println("worker=" + Arrays.toString(all.getSolutionListener().getSolution(i)));
        }
        System.out.println("Optimal solutions: " + all.getSolutionListener().solutionsNo());
    }
}
