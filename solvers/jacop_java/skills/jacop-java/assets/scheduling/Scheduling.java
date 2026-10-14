// Tasks on one machine with precedences; minimise the makespan.
// Shows: CumulativeUnary as a no-overlap constraint, precedences with
// XplusClteqZ, Max for the makespan, minimising, the proof check.
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

import org.jacop.constraints.Max;
import org.jacop.constraints.XplusClteqZ;
import org.jacop.constraints.XplusCeqZ;
import org.jacop.constraints.cumulative.CumulativeUnary;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.search.DepthFirstSearch;
import org.jacop.search.IndomainMin;
import org.jacop.search.SimpleSelect;
import org.jacop.search.SmallestMin;
import org.json.JSONArray;
import org.json.JSONObject;

public class Scheduling {
    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args.length > 0 ? args[0] : "data.json")));
        JSONArray d = data.getJSONArray("duration");
        int n = d.length();
        int horizon = 0;
        int[] duration = new int[n];
        for (int i = 0; i < n; i++) {
            duration[i] = d.getInt(i);
            horizon += duration[i];
        }

        Store store = new Store();
        IntVar[] start = new IntVar[n], end = new IntVar[n], dur = new IntVar[n], use = new IntVar[n];
        for (int i = 0; i < n; i++) {
            start[i] = new IntVar(store, "start" + i, 0, horizon);
            end[i] = new IntVar(store, "end" + i, 0, horizon);
            dur[i] = new IntVar(store, duration[i], duration[i]);
            use[i] = new IntVar(store, 1, 1);
            store.impose(new XplusCeqZ(start[i], duration[i], end[i]));
        }
        // Capacity 1: no two tasks overlap.
        store.impose(new CumulativeUnary(start, dur, use, new IntVar(store, 1, 1)));
        JSONArray precedences = data.getJSONArray("precedences");
        for (int k = 0; k < precedences.length(); k++) {
            int before = precedences.getJSONArray(k).getInt(0), after = precedences.getJSONArray(k).getInt(1);
            store.impose(new XplusClteqZ(start[before], duration[before], start[after]));
        }
        IntVar makespan = new IntVar(store, "makespan", 0, horizon);
        store.impose(new Max(end, makespan));

        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setTimeOut(10);
        // Earliest start first is the usual heuristic for scheduling.
        boolean found = search.labeling(store, new SimpleSelect<>(start, new SmallestMin<>(), new IndomainMin<>()), makespan);
        if (!found) {
            System.out.println(search.timeOutOccured ? "timeout, nothing found" : "infeasible");
        } else if (search.timeOutOccured) {
            System.out.println("timeout: makespan " + makespan.value() + " is not proven optimal");
        } else {
            int[] s = new int[n];
            for (int i = 0; i < n; i++) s[i] = start[i].value();
            System.out.println("start=" + Arrays.toString(s));
            System.out.println("Makespan: " + makespan.value());
        }
    }
}
