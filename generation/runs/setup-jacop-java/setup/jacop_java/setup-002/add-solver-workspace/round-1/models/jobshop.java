import java.nio.file.*;
import java.util.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.constraints.cumulative.CumulativeUnary;
import org.jacop.search.*;
import org.json.*;

public class Jobshop {
    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args[0])));
        JSONArray jobs = data.getJSONArray("jobs");
        int nj = jobs.length();
        int[][] mach = new int[nj][], dur = new int[nj][];
        int horizon = 0, nm = 0;
        for (int j = 0; j < nj; j++) {
            JSONArray job = jobs.getJSONArray(j);
            mach[j] = new int[job.length()]; dur[j] = new int[job.length()];
            for (int k = 0; k < job.length(); k++) {
                mach[j][k] = job.getJSONArray(k).getInt(0);
                dur[j][k] = job.getJSONArray(k).getInt(1);
                horizon += dur[j][k];
                nm = Math.max(nm, mach[j][k] + 1);
            }
        }
        Store store = new Store();
        IntVar[][] start = new IntVar[nj][];
        List<IntVar> allStarts = new ArrayList<>(), ends = new ArrayList<>();
        List<List<int[]>> onMachine = new ArrayList<>();
        for (int i = 0; i < nm; i++) onMachine.add(new ArrayList<>());
        for (int j = 0; j < nj; j++) {
            start[j] = new IntVar[mach[j].length];
            for (int k = 0; k < mach[j].length; k++) {
                start[j][k] = new IntVar(store, "s" + j + "_" + k, 0, horizon);
                allStarts.add(start[j][k]);
                if (k > 0) store.impose(new XplusClteqZ(start[j][k - 1], dur[j][k - 1], start[j][k]));
                onMachine.get(mach[j][k]).add(new int[]{j, k});
            }
            int last = mach[j].length - 1;
            if (last >= 0) {
                IntVar e = new IntVar(store, "e" + j, 0, horizon);
                store.impose(new XplusCeqZ(start[j][last], dur[j][last], e));
                ends.add(e);
            }
        }
        for (List<int[]> tasks : onMachine) {
            if (tasks.size() < 2) continue;
            int t = tasks.size();
            IntVar[] s = new IntVar[t], d = new IntVar[t], r = new IntVar[t];
            for (int i = 0; i < t; i++) {
                int j = tasks.get(i)[0], k = tasks.get(i)[1];
                s[i] = start[j][k];
                d[i] = new IntVar(store, dur[j][k], dur[j][k]);
                r[i] = new IntVar(store, 1, 1);
            }
            store.impose(new CumulativeUnary(s, d, r, new IntVar(store, 1, 1)));
        }
        IntVar makespan = new IntVar(store, "makespan", 0, horizon);
        if (ends.isEmpty()) store.impose(new XeqC(makespan, 0));
        else store.impose(new Max(ends.toArray(new IntVar[0]), makespan));
        IntVar[] vars = allStarts.toArray(new IntVar[0]);
        if (vars.length == 0) { System.out.println(new JSONObject().put("start", new JSONArray(new int[nj][0]))); return; }
        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setTimeOut(50);
        boolean found = search.labeling(store, new SimpleSelect<>(vars, new SmallestMin<>(), new IndomainMin<>()), makespan);
        if (!found || search.timeOutOccured) { System.err.println("no proven optimum"); return; }
        JSONArray out = new JSONArray();
        for (int j = 0; j < nj; j++) {
            JSONArray row = new JSONArray();
            for (IntVar x : start[j]) row.put(x.value());
            out.put(row);
        }
        System.out.println(new JSONObject().put("start", out));
        System.err.println("makespan " + makespan.value());
    }
}
