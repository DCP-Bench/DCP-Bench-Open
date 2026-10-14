import org.jacop.constraints.XplusYeqC;
import org.jacop.constraints.XplusYeqZ;
import org.jacop.constraints.XplusYgtC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.json.JSONObject;

import dcp.jacop.Model;

public class Submission {
    public static Model build(JSONObject inst, Store store) {
        int n = inst.getInt("n");
        IntVar x = new IntVar(store, "x", 0, n);
        IntVar y = new IntVar(store, "y", 0, n);
        Model m = new Model().put("x", x).put("y", y);
        if (inst.getBoolean("optimize")) {
            // x + y >= n, written as x + y > n - 1.
            store.impose(new XplusYgtC(x, y, n - 1));
            IntVar total = new IntVar(store, "total", 0, 2 * n);
            store.impose(new XplusYeqZ(x, y, total));
            m.minimize(total);
        } else {
            store.impose(new XplusYeqC(x, y, n));
        }
        return m;
    }
}
