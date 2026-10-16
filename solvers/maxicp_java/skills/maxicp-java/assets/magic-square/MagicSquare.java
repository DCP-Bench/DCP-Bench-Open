import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Magic squares of order n: the numbers 1..n*n fill the grid once each, and every row,
// column and both diagonals add up to the same magic sum. Every variable is an output,
// so each solution is distinct and no no-good is needed.
public class MagicSquare {
    public static void main(String[] args) {
        solve(3);
        solve(2);
    }

    static void solve(int n) {
        CPSolver cp = CPFactory.makeSolver();
        int cells = n * n;
        int magic = n * (cells + 1) / 2;
        CPIntVar[] sq = CPFactory.makeIntVarArray(cp, cells, 1, cells);
        CPIntVar[][] grid = new CPIntVar[n][n];
        for (int r = 0; r < n; r++)
            for (int c = 0; c < n; c++) grid[r][c] = sq[r * n + c];

        // all cells hold different numbers
        cp.post(allDifferent(sq));

        // every row adds up to the magic sum
        for (int r = 0; r < n; r++) cp.post(sum(grid[r], magic));

        // every column adds up to the magic sum
        for (int c = 0; c < n; c++) {
            CPIntVar[] column = new CPIntVar[n];
            for (int r = 0; r < n; r++) column[r] = grid[r][c];
            cp.post(sum(column, magic));
        }

        // both diagonals add up to the magic sum
        CPIntVar[] main = new CPIntVar[n];
        CPIntVar[] anti = new CPIntVar[n];
        for (int i = 0; i < n; i++) {
            main[i] = grid[i][i];
            anti[i] = grid[i][n - 1 - i];
        }
        cp.post(sum(main, magic));
        cp.post(sum(anti, magic));

        int[] count = {0};
        DFSearch search = CPFactory.makeDfs(cp, firstFailBinary(sq));
        search.onSolution(() -> count[0]++);
        SearchStatistics stats = search.solve();
        System.out.println("Order " + n + ": " + count[0] + " solutions, search completed: " + stats.isCompleted());
    }
}
