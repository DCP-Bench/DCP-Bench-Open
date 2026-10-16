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

// Print every subset of items that is within the capacity and reaches the best total value.
public class KnapsackAllOptimal {
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

            // find the best value
            int[] optimum = {0};
            DFSearch search = makeDfs(cp, firstFailBinary(take));
            search.onSolution(() -> optimum[0] = value.min());
            SearchStatistics stats = search.optimize(cp.maximize(value));
            if (stats.numberOfSolutions() == 0) {
                System.out.println("{\"status\": \"unsatisfiable\"}");
                return;
            }
            if (!stats.isCompleted()) {
                System.out.println("Optimum not proven");
                return;
            }
            // every listed selection must reach the optimum
            cp.post(eq(value, optimum[0]));

            // list every optimal selection, forbidding each one found
            while (true) {
                int[] found = new int[n];
                DFSearch all = makeDfs(cp, firstFailBinary(take));
                all.onSolution(() -> {
                    for (int i = 0; i < n; i++) found[i] = take[i].min();
                });
                SearchStatistics next = all.solve(s -> s.numberOfSolutions() >= 1);
                if (next.numberOfSolutions() == 0) break;
                System.out.println("{\"take\": " + Arrays.toString(found) + "}");
                CPBoolVar[] differ = new CPBoolVar[n];
                for (int i = 0; i < n; i++) differ[i] = not(isEq(take[i], found[i]));
                try {
                    cp.post(or(differ));
                } catch (InconsistencyException last) {
                    break;
                }
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
