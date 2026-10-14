// Every subset of `values` that sums to `target`, each printed once.
// Shows: reading JSON with org.json, BooleanVar, LinearInt, an auxiliary
// variable, and searchAll with a listener that de-duplicates on the outputs.
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;

import org.jacop.constraints.LinearInt;
import org.jacop.constraints.SumInt;
import org.jacop.core.BooleanVar;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.DepthFirstSearch;
import org.jacop.search.IndomainMin;
import org.jacop.search.Search;
import org.jacop.search.SelectChoicePoint;
import org.jacop.search.SimpleSelect;
import org.jacop.search.SimpleSolutionListener;
import org.json.JSONArray;
import org.json.JSONObject;

public class AllSolutions {
    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args.length > 0 ? args[0] : "data.json")));
        JSONArray valuesJson = data.getJSONArray("values");
        int n = valuesJson.length();
        int[] values = new int[n];
        for (int i = 0; i < n; i++) values[i] = valuesJson.getInt(i);
        int target = data.getInt("target");

        Store store = new Store();
        BooleanVar[] take = new BooleanVar[n];
        for (int i = 0; i < n; i++) take[i] = new BooleanVar(store, "take" + i);
        store.impose(new LinearInt(take, values, "==", target));
        // Auxiliary: how many items are taken. Labelled too, it is not an output.
        IntVar count = new IntVar(store, "count", 0, n);
        store.impose(new SumInt(take, "==", count));

        IntVar[] all = new IntVar[n + 1];
        System.arraycopy(take, 0, all, 0, n);
        all[n] = count;

        Set<List<Integer>> seen = new LinkedHashSet<>();
        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setSolutionListener(new SimpleSolutionListener<IntVar>() {
            @Override
            public boolean executeAfterSolution(Search<IntVar> s, SelectChoicePoint<IntVar> select) {
                boolean result = super.executeAfterSolution(s, select);
                List<Integer> chosen = new ArrayList<>();
                for (BooleanVar t : take) chosen.add(t.value());
                if (seen.add(chosen)) System.out.println("take=" + chosen);
                return result;
            }
        });
        search.getSolutionListener().searchAll(true);
        search.getSolutionListener().recordSolutions(false);
        boolean found = search.labeling(store, new SimpleSelect<>(all, null, new IndomainMin<>()));
        if (!found) System.out.println("no solution");
        System.out.println("Distinct solutions: " + seen.size());
    }
}
