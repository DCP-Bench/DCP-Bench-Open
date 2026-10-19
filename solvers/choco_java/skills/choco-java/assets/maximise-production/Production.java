// Make whole units of products A and B. A earns 3 and needs 2 labour hours and 1 kg of
// material; B earns 2 and needs 1 hour and 3 kg. There are 10 hours and 15 kg. Maximise
// the profit. Shows: scalar for the resource limits, a profit variable as the
// objective, maximisation with setObjective(MAXIMIZE, ...), and the proof check.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.SearchState;
import org.chocosolver.solver.variables.IntVar;

public class Production {
    public static void main(String[] args) {
        Model m = new Model("production");
        IntVar a = m.intVar("A", 0, 10);
        IntVar b = m.intVar("B", 0, 10);

        // labour: 2 hours per A, 1 hour per B, at most 10 hours
        m.scalar(new IntVar[]{a, b}, new int[]{2, 1}, "<=", 10).post();
        // material: 1 kg per A, 3 kg per B, at most 15 kg
        m.scalar(new IntVar[]{a, b}, new int[]{1, 3}, "<=", 15).post();

        // profit: 3 per A, 2 per B
        IntVar profit = m.intVar("profit", 0, 100, true);
        m.scalar(new IntVar[]{a, b}, new int[]{3, 2}, "=", profit).post();
        m.setObjective(Model.MAXIMIZE, profit);

        int best = -1, bestA = -1, bestB = -1;
        while (m.getSolver().solve()) {
            best = profit.getValue();
            bestA = a.getValue();
            bestB = b.getValue();
        }
        if (best < 0) {
            System.out.println("infeasible");
        } else if (m.getSolver().getSearchState() != SearchState.TERMINATED) {
            System.out.println("timeout: best found " + best + " is not proven optimal");
        } else {
            System.out.println("Make A: " + bestA + " B: " + bestB);
            System.out.println("Maximum profit: " + best);
        }
    }
}
