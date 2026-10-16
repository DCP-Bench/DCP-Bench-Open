import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.IntObjective;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Choose projects from a JSON file within the budget, maximising the profit.
// Usage: java ProjectSelection.java [data.json]
public class ProjectSelection {
    public static void main(String[] args) throws Exception {
        String file = args.length > 0 ? args[0] : "data.json";
        JsonObject data = JsonParser.parseString(Files.readString(Path.of(file))).getAsJsonObject();
        // every size comes from the data; keys the model does not use (name, note) are ignored
        String[] names = strings(data.getAsJsonArray("names"));
        int[] cost = ints(data.getAsJsonArray("cost"));
        int[] profit = ints(data.getAsJsonArray("profit"));
        int budget = data.get("budget").getAsInt();
        int n = cost.length;

        CPSolver cp = CPFactory.makeSolver();
        CPBoolVar[] take = CPFactory.makeBoolVarArray(cp, n);

        // the chosen projects cost no more than the budget
        CPIntVar[] spend = new CPIntVar[n];
        for (int i = 0; i < n; i++) spend[i] = mul(take[i], cost[i]);
        cp.post(le(sum(spend), budget));

        // at most one project from each group; the groups have different sizes
        for (JsonElement group : data.getAsJsonArray("groups")) {
            JsonArray members = group.getAsJsonArray();
            CPIntVar[] chosen = new CPIntVar[members.size()];
            for (int k = 0; k < chosen.length; k++) chosen[k] = take[members.get(k).getAsInt()];
            cp.post(le(sum(chosen), 1));
        }

        // the profit of the chosen projects
        CPIntVar[] gain = new CPIntVar[n];
        for (int i = 0; i < n; i++) gain[i] = mul(take[i], profit[i]);
        CPIntVar value = sum(gain);

        DFSearch search = CPFactory.makeDfs(cp, firstFailBinary(take));
        int[] best = new int[n];
        int[] bestValue = {0};
        search.onSolution(() -> {
            for (int i = 0; i < n; i++) best[i] = take[i].min();
            bestValue[0] = value.min();
        });
        IntObjective objective = cp.maximize(value);
        SearchStatistics stats = search.optimize(objective);

        StringBuilder items = new StringBuilder();
        for (int i = 0; i < n; i++) if (best[i] == 1) items.append(items.length() > 0 ? " " : "").append(names[i]);
        System.out.println("Best value: " + bestValue[0]);
        System.out.println("Items: " + items);
        System.out.println("Proven optimal: " + stats.isCompleted());
    }

    static int[] ints(JsonArray array) {
        int[] values = new int[array.size()];
        for (int i = 0; i < values.length; i++) values[i] = array.get(i).getAsInt();
        return values;
    }

    static String[] strings(JsonArray array) {
        String[] values = new String[array.size()];
        for (int i = 0; i < values.length; i++) values[i] = array.get(i).getAsString();
        return values;
    }
}
