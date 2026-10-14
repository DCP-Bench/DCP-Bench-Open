import java.nio.file.*;
import java.util.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;
import org.json.*;

public class KnapsackAllOptimal {
    static int n, cap, vsum;
    static int[] w, v;
    record Built(Store store, BooleanVar[] take, IntVar total) {}

    static Built build() {
        Store store = new Store();
        BooleanVar[] take = new BooleanVar[n];
        for (int i = 0; i < n; i++) take[i] = new BooleanVar(store, "t" + i);
        store.impose(new LinearInt(take, w, "<=", cap));
        IntVar total = new IntVar(store, "total", 0, vsum);
        store.impose(new LinearInt(take, v, "==", total));
        return new Built(store, take, total);
    }

    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args[0])));
        JSONArray wj = data.getJSONArray("weights"), vj = data.getJSONArray("values");
        n = wj.length(); cap = data.getInt("capacity");
        w = new int[n]; v = new int[n];
        for (int i = 0; i < n; i++) { w[i] = wj.getInt(i); v[i] = vj.getInt(i); vsum += v[i]; }
        if (n == 0) { System.out.println("{\"take\": []}"); return; }

        Built m = build();
        IntVar neg = new IntVar(m.store(), "neg", -vsum, 0);
        m.store().impose(new XmulCeqZ(m.total(), -1, neg));
        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setTimeOut(25);
        boolean found = search.labeling(m.store(), new SimpleSelect<>(m.take(), null, new IndomainMax<>()), neg);
        if (!found || search.timeOutOccured) { System.err.println("no proven optimum"); return; }
        int best = m.total().value();

        Built e = build();
        e.store().impose(new XeqC(e.total(), best));
        Set<List<Integer>> seen = new HashSet<>();
        DepthFirstSearch<IntVar> all = new DepthFirstSearch<>();
        all.setPrintInfo(false);
        all.setTimeOut(25);
        all.setSolutionListener(new SimpleSolutionListener<IntVar>() {
            @Override
            public boolean executeAfterSolution(Search<IntVar> s, SelectChoicePoint<IntVar> select) {
                boolean r = super.executeAfterSolution(s, select);
                List<Integer> sol = new ArrayList<>();
                for (BooleanVar t : e.take()) sol.add(t.value());
                if (seen.add(sol)) System.out.println(new JSONObject().put("take", new JSONArray(sol)));
                return r;
            }
        });
        all.getSolutionListener().searchAll(true);
        all.getSolutionListener().recordSolutions(false);
        all.labeling(e.store(), new SimpleSelect<>(e.take(), null, new IndomainMin<>()));
        if (all.timeOutOccured) System.err.println("timeout: enumeration incomplete");
    }
}
