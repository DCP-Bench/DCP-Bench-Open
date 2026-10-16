import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

public class QuickStart {
    public static void main(String[] args) {
        CPSolver cp = makeSolver();
        CPIntVar x = makeIntVar(cp, 0, 2);
        CPIntVar y = makeIntVar(cp, 0, 2);
        // x and y add up to 2
        cp.post(eq(sum(x, y), 2));
        DFSearch search = makeDfs(cp, firstFailBinary(x, y));
        search.onSolution(() -> System.out.println("x=" + x.min() + " y=" + y.min()));
        SearchStatistics stats = search.solve();
        System.out.println("solutions: " + stats.numberOfSolutions() + ", completed: " + stats.isCompleted());
    }
}
