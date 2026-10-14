import java.nio.file.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;
import org.json.*;

public class Knapsack {
    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args[0])));
        JSONArray wj = data.getJSONArray("weights"), vj = data.getJSONArray("values");
        int n = wj.length(), cap = data.getInt("capacity");
        int[] w = new int[n], v = new int[n];
        int vsum = 0;
        for (int i = 0; i < n; i++) { w[i] = wj.getInt(i); v[i] = vj.getInt(i); vsum += v[i]; }
        if (n == 0) { System.out.println("{\"take\": []}"); return; }
        Store store = new Store();
        BooleanVar[] take = new BooleanVar[n];
        for (int i = 0; i < n; i++) take[i] = new BooleanVar(store, "t" + i);
        store.impose(new LinearInt(take, w, "<=", cap));
        IntVar total = new IntVar(store, "total", 0, vsum);
        store.impose(new LinearInt(take, v, "==", total));
        IntVar neg = new IntVar(store, "neg", -vsum, 0);
        store.impose(new XmulCeqZ(total, -1, neg));
        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setTimeOut(50);
        boolean found = search.labeling(store, new SimpleSelect<>(take, null, new IndomainMax<>()), neg);
        if (!found || search.timeOutOccured) { System.err.println("no proven optimum"); return; }
        JSONArray a = new JSONArray();
        for (BooleanVar t : take) a.put(t.value());
        System.out.println(new JSONObject().put("take", a));
    }
}
