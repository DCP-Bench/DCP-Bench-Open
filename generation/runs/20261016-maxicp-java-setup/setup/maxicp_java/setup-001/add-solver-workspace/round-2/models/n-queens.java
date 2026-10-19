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

// Place n queens so that no two share a row, a column or a diagonal.
public class NQueens {
    public static void main(String[] args) throws Exception {
        int n = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject().get("n").getAsInt();

        CPSolver cp = CPFactory.makeSolver();
        // queens[i] is the column of the queen in row i
        CPIntVar[] queens = CPFactory.makeIntVarArray(cp, n, n);

        // no two queens share a column
        cp.post(allDifferent(queens));

        // no two queens share a diagonal: column plus row, and column minus row, are all different
        CPIntVar[] up = new CPIntVar[n];
        CPIntVar[] down = new CPIntVar[n];
        for (int i = 0; i < n; i++) {
            up[i] = plus(queens[i], i);
            down[i] = minus(queens[i], i);
        }
        cp.post(allDifferent(up));
        cp.post(allDifferent(down));

        // one placement is enough
        int[] found = new int[n];
        DFSearch search = CPFactory.makeDfs(cp, firstFailBinary(queens));
        search.onSolution(() -> {
            for (int i = 0; i < n; i++) found[i] = queens[i].min();
        });
        SearchStatistics stats = search.solve(s -> s.numberOfSolutions() >= 1);
        if (stats.numberOfSolutions() == 0) {
            System.out.println("{\"status\": \"unsatisfiable\"}");
            return;
        }
        System.out.println("{\"queens\": " + Arrays.toString(found) + "}");
    }
}
