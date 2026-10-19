// Give 5 tasks distinct slots when only 4 slots exist. Shows: allDifferent, and what an
// infeasible model looks like: solve() returns false at once, with no solution.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;

public class Pigeonhole {
    public static void main(String[] args) {
        Model m = new Model("pigeonhole");
        IntVar[] slot = m.intVarArray("slot", 5, 0, 3);

        // every task has its own slot
        m.allDifferent(slot, "AC").post();

        if (m.getSolver().solve()) System.out.println("solution found");
        else System.out.println("infeasible");
    }
}
