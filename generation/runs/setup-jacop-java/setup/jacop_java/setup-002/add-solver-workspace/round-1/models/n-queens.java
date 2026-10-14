import java.nio.file.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;
import org.json.*;

public class NQueens {
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
        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setTimeOut(50);
        boolean found = search.labeling(store, new SimpleSelect<>(q, new SmallestDomain<>(), new IndomainMiddle<>()));
        if (found) {
            JSONArray a = new JSONArray();
            for (IntVar v : q) a.put(v.value());
            System.out.println(new JSONObject().put("queens", a));
        } else if (!search.timeOutOccured) {
            System.out.println("{\"status\": \"unsatisfiable\"}");
        } else System.err.println("timeout");
    }
}
