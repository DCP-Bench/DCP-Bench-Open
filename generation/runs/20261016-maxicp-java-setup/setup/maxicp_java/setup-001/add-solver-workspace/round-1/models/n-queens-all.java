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

// Place n queens so that no two share a row, column or diagonal. Print every solution.
public class NQueensAll {
    public static void main(String[] args) throws Exception {
        int n = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject().get("n").getAsInt();
        CPSolver cp = makeSolver();
        try {
            // q[i]: the column of the queen in row i
            CPIntVar[] q = makeIntVarArray(cp, n, 0, n - 1);
            // no two queens share a column
            cp.post(allDifferent(q));
            // no two queens share a diagonal
            CPIntVar[] up = new CPIntVar[n];
            CPIntVar[] down = new CPIntVar[n];
            for (int i = 0; i < n; i++) {
                up[i] = plus(q[i], i);
                down[i] = plus(q[i], -i);
            }
            cp.post(allDifferent(up));
            cp.post(allDifferent(down));

            // every column is fixed by the branching, so each solution is printed once
            DFSearch search = makeDfs(cp, firstFailBinary(q));
            search.onSolution(() -> {
                int[] sol = new int[n];
                for (int i = 0; i < n; i++) sol[i] = q[i].min();
                System.out.println("{\"queens\": " + Arrays.toString(sol) + "}");
            });
            SearchStatistics stats = search.solve();
            if (stats.numberOfSolutions() == 0) {
                System.out.println("{\"status\": \"unsatisfiable\"}");
            }
        } catch (InconsistencyException e) {
            System.out.println("{\"status\": \"unsatisfiable\"}");
        }
    }
}
