// Pack a camping trip: take items from data.json within the weight capacity, take every
// item marked "required", take at most one item from each group, and maximise the value.
// Shows: reading a JSON file with Gson, every size taken from the data (the item count,
// the groups, which may be ragged), JSON booleans read as 1 and 0, and maximisation.
import java.nio.file.Files;
import java.nio.file.Path;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.SearchState;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;

public class Knapsack {
    public static void main(String[] args) throws Exception {
        // the file name is the first argument; data.json is the default
        JsonObject data = JsonParser.parseString(
                Files.readString(Path.of(args.length > 0 ? args[0] : "data.json"))).getAsJsonObject();
        int capacity = data.get("capacity").getAsInt();
        // keys the model does not use, such as "name", are simply not read

        JsonArray items = data.getAsJsonArray("items");
        int n = items.size();                       // the item count comes from the data
        String[] name = new String[n];
        int[] weight = new int[n], value = new int[n], required = new int[n];
        for (int i = 0; i < n; i++) {
            JsonObject item = items.get(i).getAsJsonObject();
            name[i] = item.get("name").getAsString();
            weight[i] = item.get("weight").getAsInt();
            value[i] = item.get("value").getAsInt();
            required[i] = item.get("required").getAsBoolean() ? 1 : 0;   // JSON true/false as 1/0
        }

        Model m = new Model("camping");
        BoolVar[] take = m.boolVarArray("take", n);

        // the chosen items weigh at most the capacity
        m.scalar(take, weight, "<=", capacity).post();

        // a required item is always taken
        for (int i = 0; i < n; i++) if (required[i] == 1) m.arithm(take[i], "=", 1).post();

        // at most one item from each group; the groups may have different sizes
        JsonArray groups = data.getAsJsonArray("groups");
        for (JsonElement g : groups) {
            JsonArray members = g.getAsJsonArray();
            IntVar[] group = new IntVar[members.size()];
            for (int k = 0; k < members.size(); k++) group[k] = take[members.get(k).getAsInt()];
            m.sum(group, "<=", 1).post();
        }

        // maximise the total value of the taken items
        int total = 0;
        for (int v : value) total += v;
        IntVar best = m.intVar("value", 0, total, true);
        m.scalar(take, value, "=", best).post();
        m.setObjective(Model.MAXIMIZE, best);

        int bestValue = -1;
        StringBuilder chosen = new StringBuilder();
        while (m.getSolver().solve()) {
            bestValue = best.getValue();
            chosen.setLength(0);
            for (int i = 0; i < n; i++) if (take[i].getValue() == 1) chosen.append(name[i]).append(' ');
        }
        if (bestValue < 0) {
            System.out.println("infeasible");
        } else if (m.getSolver().getSearchState() != SearchState.TERMINATED) {
            System.out.println("timeout: best found " + bestValue + " is not proven optimal");
        } else {
            System.out.println("Best value: " + bestValue);
            System.out.println("Items: " + chosen.toString().trim());
        }
    }
}
