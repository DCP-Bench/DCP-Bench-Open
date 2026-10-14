import java.nio.file.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;
import org.json.*;

public class Main {
    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args[0])));  // {"n": 4}
        int n = data.getInt("n");                // read only the keys you need
        Store store = new Store();
        IntVar x = new IntVar(store, "x", 0, n), y = new IntVar(store, "y", 0, n);
        store.impose(new XplusYeqC(x, y, n));
        store.impose(new XneqY(x, y));

        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);              // otherwise it prints to stdout
        search.setTimeOut(10);                   // seconds
        SelectChoicePoint<IntVar> select =
            new SimpleSelect<>(new IntVar[]{x, y}, new SmallestDomain<>(), new IndomainMin<>());
        boolean found = search.labeling(store, select);
        if (found) System.out.println("x=" + x.value() + " y=" + y.value());
        else System.out.println(search.timeOutOccured ? "timeout" : "infeasible");
    }
}
