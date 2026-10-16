import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Print every subset that reaches the best total value within the capacity.
public class KnapsackAllOptimal {
    public static void main(String[] args) throws Exception {
        var data = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        int[] weights = ints(data.getAsJsonArray("weights"));
        int[] values = ints(data.getAsJsonArray("values"));
        int capacity = data.get("capacity").getAsInt();
        int n = weights.length;

        CPSolver cp = CPFactory.makeSolver();
        // take[i] is 1 when item i is chosen; every take variable is an output
        CPBoolVar[] take = CPFactory.makeBoolVarArray(cp, n);

        // the chosen items weigh no more than the capacity
        CPIntVar[] weight = new CPIntVar[n];
        for (int i = 0; i < n; i++) weight[i] = mul(take[i], weights[i]);
        cp.post(le(sum(weight), capacity));

        // the total value of the chosen items
        CPIntVar[] gain = new CPIntVar[n];
        for (int i = 0; i < n; i++) gain[i] = mul(take[i], values[i]);
        CPIntVar total = sum(gain);

        // find the best value
        int[] bestValue = {0};
        DFSearch search = CPFactory.makeDfs(cp, firstFailBinary(take));
        search.onSolution(() -> bestValue[0] = total.min());
        SearchStatistics stats = search.optimize(cp.maximize(total));
        if (!stats.isCompleted()) {
            System.out.println("Optimum not proven");
            return;
        }

        // only subsets that reach the best value are optimal
        cp.post(eq(total, bestValue[0]));

        // enumerate every optimal subset
        DFSearch all = CPFactory.makeDfs(cp, firstFailBinary(take));
        all.onSolution(() -> {
            int[] chosen = new int[n];
            for (int i = 0; i < n; i++) chosen[i] = take[i].min();
            System.out.println("{\"take\": " + Arrays.toString(chosen) + "}");
        });
        all.solve();
    }

    static int[] ints(JsonArray array) {
        int[] out = new int[array.size()];
        for (int i = 0; i < out.length; i++) out[i] = array.get(i).getAsInt();
        return out;
    }
}
