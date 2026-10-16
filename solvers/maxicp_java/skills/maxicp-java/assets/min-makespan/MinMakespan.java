import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import org.maxicp.util.exception.InconsistencyException;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Assign jobs to machines so that the last machine finishes as early as possible, then
// list every assignment that reaches this makespan.
public class MinMakespan {
    public static void main(String[] args) {
        int[] duration = {3, 5, 2, 7, 4, 6};
        int machines = 3;
        int n = duration.length;

        CPSolver cp = CPFactory.makeSolver();
        // machine[j]: the machine that runs job j
        CPIntVar[] machine = CPFactory.makeIntVarArray(cp, n, machines);

        // the load of a machine is the total duration of the jobs on it
        CPIntVar[] load = new CPIntVar[machines];
        for (int k = 0; k < machines; k++) {
            CPIntVar[] part = new CPIntVar[n];
            for (int j = 0; j < n; j++) part[j] = mul(isEq(machine[j], k), duration[j]);
            load[k] = sum(part);
        }
        // the makespan is the largest load
        CPIntVar makespan = max(load);

        // optimum: the search keeps the last solution, which is optimal when the search completes
        int[] optimum = {0};
        DFSearch search = CPFactory.makeDfs(cp, firstFailBinary(machine));
        search.onSolution(() -> optimum[0] = makespan.min());
        SearchStatistics stats = search.optimize(cp.minimize(makespan));
        if (!stats.isCompleted()) {
            System.out.println("Optimum not proven");
            return;
        }
        System.out.println("Optimal makespan: " + optimum[0]);

        // every optimal assignment: fix the makespan, then forbid each assignment found
        cp.post(eq(makespan, optimum[0]));
        List<String> found = new ArrayList<>();
        while (true) {
            int[] values = new int[n];
            DFSearch all = CPFactory.makeDfs(cp, firstFailBinary(machine));
            all.onSolution(() -> {
                for (int j = 0; j < n; j++) values[j] = machine[j].min();
            });
            SearchStatistics next = all.solve(s -> s.numberOfSolutions() >= 1);
            if (next.numberOfSolutions() == 0) break;
            found.add(Arrays.toString(values));
            CPBoolVar[] differ = new CPBoolVar[n];
            for (int j = 0; j < n; j++) differ[j] = not(isEq(machine[j], values[j]));
            try {
                cp.post(or(differ));
            } catch (InconsistencyException last) {
                break;
            }
        }
        System.out.println("Optimal assignments: " + found.size());
        System.out.println("First: " + found.get(0));
    }
}
