import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Which misuses raise which exception, and what their messages say.
public class Probe3 {
    interface Attempt { void run() throws Exception; }

    static void attempt(String name, Attempt a) {
        try {
            a.run();
            System.out.println(name + ": no exception");
        } catch (Throwable t) {
            System.out.println(name + ": " + t.getClass().getName() + " msg=[" + t.getMessage() + "]");
        }
    }

    public static void main(String[] args) {
        attempt("empty domain", () -> { CPSolver cp = CPFactory.makeSolver(); CPFactory.makeIntVar(cp, 3, 1); });
        attempt("negative array size", () -> { CPSolver cp = CPFactory.makeSolver(); CPFactory.makeIntVarArray(cp, -1, 2); });
        attempt("element index out of range", () -> {
            CPSolver cp = CPFactory.makeSolver();
            CPIntVar y = CPFactory.makeIntVar(cp, 0, 5);
            CPIntVar e = element(new int[]{1, 2}, y); System.out.println("  view size " + e.size());
            System.out.println("  posted; y in " + y.min() + ".." + y.max());
        });
        attempt("allDifferent on empty array", () -> { CPSolver cp = CPFactory.makeSolver(); cp.post(allDifferent(new CPIntVar[0])); });
        attempt("table row arity mismatch", () -> {
            CPSolver cp = CPFactory.makeSolver();
            CPIntVar x = CPFactory.makeIntVar(cp, 0, 2);
            cp.post(table(new CPIntVar[]{x, x}, new int[][]{{1}}));
        });
        attempt("null objective", () -> { CPSolver cp = CPFactory.makeSolver(); cp.minimize(null); });
        attempt("search with no branching vars", () -> {
            CPSolver cp = CPFactory.makeSolver();
            DFSearch d = CPFactory.makeDfs(cp, () -> EMPTY);
            SearchStatistics s = d.solve();
            System.out.println("  solutions=" + s.numberOfSolutions() + " completed=" + s.isCompleted());
        });
        attempt("int overflow var", () -> { CPSolver cp = CPFactory.makeSolver(); CPFactory.makeIntVar(cp, 0, 40000000000L > 0 ? Integer.MAX_VALUE : 0); });
    }
}
