import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

public class Probe1 {
    static SearchStatistics nqueens(int n, String heur) {
        CPSolver cp = CPFactory.makeSolver();
        CPIntVar[] q = CPFactory.makeIntVarArray(cp, n, n);
        CPIntVar[] qL = CPFactory.makeIntVarArray(n, i -> minus(q[i], i));
        CPIntVar[] qR = CPFactory.makeIntVarArray(n, i -> plus(q[i], i));
        cp.post(allDifferent(q));
        cp.post(allDifferent(qL));
        cp.post(allDifferent(qR));
        java.util.function.Supplier<Runnable[]> b = switch (heur) {
            case "binary" -> firstFailBinary(q);
            case "nary" -> firstFailNary(q);
            case "heurNary" -> heuristicNary(minDomVariableSelector(q));
            default -> throw new IllegalArgumentException(heur);
        };
        DFSearch dfs = CPFactory.makeDfs(cp, b);
        return dfs.solve();
    }

    public static void main(String[] args) {
        for (String h : new String[]{"binary", "nary", "heurNary"}) {
            try {
                SearchStatistics s = nqueens(8, h);
                System.out.println(h + " 8-queens: " + s + " completed=" + s.isCompleted());
            } catch (Throwable t) {
                System.out.println(h + " 8-queens threw " + t);
            }
        }
        for (String h : new String[]{"binary", "nary", "heurNary"}) {
            try {
                CPSolver cp = CPFactory.makeSolver();
                CPIntVar x = CPFactory.makeIntVar(cp, 0, 2);
                java.util.function.Supplier<Runnable[]> b = switch (h) {
                    case "binary" -> firstFailBinary(x);
                    case "nary" -> firstFailNary(x);
                    default -> heuristicNary(minDomVariableSelector(x));
                };
                DFSearch dfs = CPFactory.makeDfs(cp, b);
                StringBuilder seen = new StringBuilder();
                dfs.onSolution(() -> seen.append(x.min()).append(' '));
                SearchStatistics s = dfs.solve();
                System.out.println(h + " domain {0,1,2}: solutions x=[" + seen + "] " + s);
            } catch (Throwable t) {
                System.out.println(h + " domain threw " + t);
            }
        }
    }
}
