import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Colour the nodes so that adjacent nodes differ, using as few colours as possible.
public class GraphColouring {
    public static void main(String[] args) throws Exception {
        var data = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        int n = data.get("n_nodes").getAsInt();
        JsonArray edges = data.getAsJsonArray("edges");

        CPSolver cp = CPFactory.makeSolver();
        // colour[v] is the colour of node v, from 0 to n-1
        CPIntVar[] colour = CPFactory.makeIntVarArray(cp, n, n);

        // the two endpoints of every edge get different colours
        for (int e = 0; e < edges.size(); e++) {
            JsonArray edge = edges.get(e).getAsJsonArray();
            cp.post(neq(colour[edge.get(0).getAsInt()], colour[edge.get(1).getAsInt()]));
        }

        // the number of colours is the largest colour used plus one
        CPIntVar used = plus(max(colour), 1);

        int[] best = new int[n];
        DFSearch search = CPFactory.makeDfs(cp, firstFailBinary(colour));
        search.onSolution(() -> {
            for (int v = 0; v < n; v++) best[v] = colour[v].min();
        });
        SearchStatistics stats = search.optimize(cp.minimize(used));
        if (!stats.isCompleted()) {
            System.out.println("Optimum not proven");
            return;
        }
        System.out.println("{\"colour\": " + Arrays.toString(best) + "}");
    }
}
