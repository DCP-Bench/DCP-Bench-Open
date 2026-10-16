import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Place n queens so that no two share a row, a column or a diagonal; print every placement.
public class NQueensAll {
    public static void main(String[] args) throws Exception {
        int n = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject().get("n").getAsInt();

        CPSolver cp = CPFactory.makeSolver();
        // queens[i] is the column of the queen in row i; these are the only variables
        CPIntVar[] queens = CPFactory.makeIntVarArray(cp, n, n);

        // no two queens share a column
        cp.post(allDifferent(queens));

        // no two queens share a diagonal
        CPIntVar[] up = new CPIntVar[n];
        CPIntVar[] down = new CPIntVar[n];
        for (int i = 0; i < n; i++) {
            up[i] = plus(queens[i], i);
            down[i] = minus(queens[i], i);
        }
        cp.post(allDifferent(up));
        cp.post(allDifferent(down));

        // every placement is one solution, printed once
        DFSearch search = CPFactory.makeDfs(cp, firstFailBinary(queens));
        search.onSolution(() -> {
            int[] values = new int[n];
            for (int i = 0; i < n; i++) values[i] = queens[i].min();
            System.out.println("{\"queens\": " + Arrays.toString(values) + "}");
        });
        search.solve();
    }
}
