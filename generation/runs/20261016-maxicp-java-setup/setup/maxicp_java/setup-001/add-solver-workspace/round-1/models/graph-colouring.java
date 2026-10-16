import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import org.maxicp.util.exception.InconsistencyException;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Colour the nodes so that adjacent nodes differ, using as few colours as possible.
// Minimising the largest colour index gives the fewest colours, since colours can be renamed.
public class GraphColouring {
    public static void main(String[] args) throws Exception {
        var data = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        int n = data.get("n_nodes").getAsInt();
        JsonArray edges = data.getAsJsonArray("edges");

        CPSolver cp = makeSolver();
        try {
            // colour[v]: the colour of node v
            CPIntVar[] colour = makeIntVarArray(cp, n, 0, n - 1);
            // the two endpoints of every edge get different colours
            for (var e : edges) {
                int u = e.getAsJsonArray().get(0).getAsInt();
                int v = e.getAsJsonArray().get(1).getAsInt();
                cp.post(allDifferent(new CPIntVar[] {colour[u], colour[v]}));
            }
            // the number of colours is the largest colour index plus one
            CPIntVar maxColour = max(colour);

            int[] best = new int[n];
            DFSearch search = makeDfs(cp, firstFailBinary(colour));
            search.onSolution(() -> {
                for (int v = 0; v < n; v++) best[v] = colour[v].min();
            });
            SearchStatistics stats = search.optimize(cp.minimize(maxColour));
            if (stats.numberOfSolutions() == 0) {
                System.out.println("{\"status\": \"unsatisfiable\"}");
            } else if (!stats.isCompleted()) {
                System.out.println("Optimum not proven");
            } else {
                System.out.println("{\"colour\": " + Arrays.toString(best) + "}");
            }
        } catch (InconsistencyException e) {
            System.out.println("{\"status\": \"unsatisfiable\"}");
        }
    }
}
