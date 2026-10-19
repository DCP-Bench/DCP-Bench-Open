// Four tasks share one resource with capacity 2: task 0 needs 1 unit, task 1 needs 1,
// task 2 needs 2 and task 3 needs 1. Task 0 must end before task 2 starts, and task 1
// before task 3. Each task runs without interruption. Minimise the makespan, the time
// the last task ends. Shows: cumulative over start times, precedences with arithm,
// the makespan as the maximum of the end times, and branching on start times.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.SearchState;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;

public class Project {
    public static void main(String[] args) {
        int[] duration = {3, 2, 2, 4};
        int[] use = {1, 1, 2, 1};
        int capacity = 2;
        int n = duration.length;
        int horizon = 0;
        for (int d : duration) horizon += d;

        Model m = new Model("project");
        IntVar[] start = m.intVarArray("start", n, 0, horizon - 1, true);
        IntVar[] end = new IntVar[n];
        for (int i = 0; i < n; i++) end[i] = m.offset(start[i], duration[i]);   // end = start + duration, a view

        // at every moment the running tasks need at most the capacity
        m.cumulative(start, duration, use, capacity).post();

        // task 0 ends before task 2 starts; task 1 ends before task 3 starts
        m.arithm(end[0], "<=", start[2]).post();
        m.arithm(end[1], "<=", start[3]).post();

        // the makespan is the time the last task ends
        IntVar makespan = m.intVar("makespan", 0, horizon, true);
        m.max(makespan, end).post();
        m.setObjective(Model.MINIMIZE, makespan);
        m.getSolver().setSearch(Search.inputOrderLBSearch(start));

        int best = -1;
        while (m.getSolver().solve()) best = makespan.getValue();
        if (best < 0) {
            System.out.println("infeasible");
        } else if (m.getSolver().getSearchState() != SearchState.TERMINATED) {
            System.out.println("timeout: best found " + best + " is not proven optimal");
        } else {
            System.out.println("Makespan: " + best);
        }
    }
}
