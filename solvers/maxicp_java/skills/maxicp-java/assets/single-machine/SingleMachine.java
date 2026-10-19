import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPIntervalVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Schedule four tasks on one machine: no two tasks overlap, some tasks must finish
// before others start, and some tasks cannot start before their release time.
// Minimise the makespan, the time the last task ends.
public class SingleMachine {
    public static void main(String[] args) {
        int[] duration = {3, 2, 4, 2};
        int[] release = {0, 0, 0, 4};
        int[][] before = {{0, 2}, {1, 3}};   // task a must end before task b starts
        int n = duration.length;

        CPSolver cp = CPFactory.makeSolver();
        CPIntervalVar[] task = new CPIntervalVar[n];
        for (int i = 0; i < n; i++) task[i] = CPFactory.makeIntervalVar(cp, false, duration[i]);   // false: the task must run

        // the machine runs one task at a time
        cp.post(noOverlap(task));

        // precedences
        for (int[] pair : before) cp.post(endBeforeStart(task[pair[0]], task[pair[1]]));

        // release times
        for (int i = 0; i < n; i++) cp.post(startAfter(task[i], release[i]));

        // the makespan is the end of the last task
        CPIntVar makespan = makespan(task);

        // branch on start times, earliest first
        CPIntVar[] starts = new CPIntVar[n];
        for (int i = 0; i < n; i++) starts[i] = start(task[i]);
        int[] when = new int[n];
        int[] best = {0};
        DFSearch search = CPFactory.makeDfs(cp, firstFailBinary(starts));
        search.onSolution(() -> {
            for (int i = 0; i < n; i++) when[i] = starts[i].min();
            best[0] = makespan.min();
        });
        SearchStatistics stats = search.optimize(cp.minimize(makespan));

        System.out.println("Makespan: " + best[0]);
        System.out.println("Starts: " + java.util.Arrays.toString(when));
        System.out.println("Proven optimal: " + stats.isCompleted());
    }
}
