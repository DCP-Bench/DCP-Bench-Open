import java.nio.file.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;
import org.json.*;

public class GraphColouring {
    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args[0])));
        int n = data.getInt("n_nodes");
        JSONArray edges = data.getJSONArray("edges");
        if (n == 0) { System.out.println("{\"colour\": []}"); return; }
        Store store = new Store();
        IntVar[] c = new IntVar[n];
        for (int i = 0; i < n; i++) c[i] = new IntVar(store, "c" + i, 0, n - 1);
        for (int k = 0; k < edges.length(); k++) {
            int a = edges.getJSONArray(k).getInt(0), b = edges.getJSONArray(k).getInt(1);
            if (a != b) store.impose(new XneqY(c[a], c[b]));
        }
        // symmetry breaking: node i uses colour <= i
        for (int i = 0; i < n; i++) store.impose(new XlteqC(c[i], i));
        IntVar maxc = new IntVar(store, "maxc", 0, n - 1);
        store.impose(new Max(c, maxc));
        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setTimeOut(50);
        boolean found = search.labeling(store, new SimpleSelect<>(c, new SmallestDomain<>(), new IndomainMin<>()), maxc);
        if (!found || search.timeOutOccured) { System.err.println("no proven optimum"); return; }
        JSONArray arr = new JSONArray();
        for (IntVar x : c) arr.put(x.value());
        System.out.println(new JSONObject().put("colour", arr));
    }
}
