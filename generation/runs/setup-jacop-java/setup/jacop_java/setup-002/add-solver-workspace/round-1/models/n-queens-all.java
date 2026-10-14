import java.nio.file.*;
import java.util.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;
import org.json.*;

public class NQueensAll {
    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args[0])));
        int n = data.getInt("n");
        Store store = new Store();
        IntVar[] q = new IntVar[n], d1 = new IntVar[n], d2 = new IntVar[n];
        for (int i = 0; i < n; i++) {
            q[i] = new IntVar(store, "q" + i, 0, n - 1);
            d1[i] = new IntVar(store, "d1_" + i, i, n - 1 + i);
            d2[i] = new IntVar(store, "d2_" + i, -i, n - 1 - i);
            store.impose(new XplusCeqZ(q[i], i, d1[i]));
            store.impose(new XplusCeqZ(q[i], -i, d2[i]));
        }
        store.impose(new Alldistinct(q));
        store.impose(new Alldifferent(d1));
        store.impose(new Alldifferent(d2));
        Set<List<Integer>> seen = new HashSet<>();
        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setTimeOut(50);
        search.setSolutionListener(new SimpleSolutionListener<IntVar>() {
            @Override
            public boolean executeAfterSolution(Search<IntVar> s, SelectChoicePoint<IntVar> select) {
                boolean r = super.executeAfterSolution(s, select);
                List<Integer> sol = new ArrayList<>();
                for (IntVar v : q) sol.add(v.value());
                if (seen.add(sol)) System.out.println(new JSONObject().put("queens", new JSONArray(sol)));
                return r;
            }
        });
        search.getSolutionListener().searchAll(true);
        search.getSolutionListener().recordSolutions(false);
        search.labeling(store, new SimpleSelect<>(q, null, new IndomainMin<>()));
        if (search.timeOutOccured) System.err.println("timeout: enumeration incomplete");
    }
}
