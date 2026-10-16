import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import org.maxicp.util.exception.InconsistencyException;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Choose items within the capacity so that the total value is as large as possible.
public class Knapsack {
    public static void main(String[] args) throws Exception {
        var data = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        int[] weights = ints(data.getAsJsonArray("weights"));
        int[] values = ints(data.getAsJsonArray("values"));
        int capacity = data.get("capacity").getAsInt();
        int n = weights.length;

        CPSolver cp = makeSolver();
        try {
            // take[i]: 1 if item i is taken
            CPBoolVar[] take = makeBoolVarArray(cp, n);
            // the taken items weigh no more than the capacity
            CPIntVar[] weight = new CPIntVar[n];
            for (int i = 0; i < n; i++) weight[i] = mul(take[i], weights[i]);
            cp.post(le(sum(weight), capacity));
            // the value of the taken items
            CPIntVar[] gain = new CPIntVar[n];
            for (int i = 0; i < n; i++) gain[i] = mul(take[i], values[i]);
            CPIntVar value = sum(gain);

            int[] best = new int[n];
            DFSearch search = makeDfs(cp, firstFailBinary(take));
            search.onSolution(() -> {
                for (int i = 0; i < n; i++) best[i] = take[i].min();
            });
            SearchStatistics stats = search.optimize(cp.maximize(value));
            if (stats.numberOfSolutions() == 0) {
                System.out.println("{\"status\": \"unsatisfiable\"}");
            } else if (!stats.isCompleted()) {
                System.out.println("Optimum not proven");
            } else {
                System.out.println("{\"take\": " + Arrays.toString(best) + "}");
            }
        } catch (InconsistencyException e) {
            System.out.println("{\"status\": \"unsatisfiable\"}");
        }
    }

    static int[] ints(JsonArray array) {
        int[] values = new int[array.size()];
        for (int i = 0; i < values.length; i++) values[i] = array.get(i).getAsInt();
        return values;
    }
}
