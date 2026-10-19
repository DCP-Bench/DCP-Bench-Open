// Three tasks on one machine: durations 2, 3 and 2, release times 0, 0 and 4 (a task
// cannot start before its release). The machine runs one task at a time. Minimise the
// makespan. Runs with lazy clause generation, which is safe here because every
// constraint is one of the checked ones: cumulative (unit heights), arithm and max.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.SettingsBuilder;
import org.chocosolver.solver.search.SearchState;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.IntVar;

public class Machine {
    public static void main(String[] args) {
        int[] duration = {2, 3, 2};
        int[] release = {0, 0, 4};
        int n = duration.length;
        int horizon = 12;

        // LCG is switched on through the settings given to the model
        Model m = new Model("machine", SettingsBuilder.init().setLCG(true));
        IntVar[] start = new IntVar[n];
        IntVar[] end = new IntVar[n];
        int[] unit = new int[n];
        for (int i = 0; i < n; i++) {
            // not before its release time
            start[i] = m.intVar("start" + i, release[i], horizon - duration[i], true);
            end[i] = m.offset(start[i], duration[i]);   // end = start + duration, a view
            unit[i] = 1;
        }

        // one task at a time on the machine: a unit-height cumulative with capacity 1
        m.cumulative(start, duration, unit, 1).post();

        IntVar makespan = m.intVar("makespan", 0, horizon, true);
        m.max(makespan, end).post();
        m.setObjective(Model.MINIMIZE, makespan);

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
