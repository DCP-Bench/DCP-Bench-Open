// Choose exactly 2 of 4 items at minimum total cost, then print every choice that
// reaches that minimum. Costs: 2, 1, 2, 5. Shows: Boolean choices with sum, a cost
// variable tied by scalar, the optimality check (TERMINATED, not STOPPED), and
// enumeration of all optimal solutions on a fresh model with the objective fixed
// to the optimum.
import java.util.ArrayList;
import java.util.List;
import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.SearchState;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;

public class Pair {
    static final int[] COST = {2, 1, 2, 5};

    /** The model and its variables; built afresh for each solve. */
    record Built(Model model, BoolVar[] pick, IntVar total) {}

    static Built build() {
        Model m = new Model("pair");
        BoolVar[] pick = m.boolVarArray("pick", COST.length);
        // exactly two items are picked
        m.sum(pick, "=", 2).post();
        // the total cost is the sum of the picked items' costs
        IntVar total = m.intVar("total", 0, 100, true);
        m.scalar(pick, COST, "=", total).post();
        return new Built(m, pick, total);
    }

    public static void main(String[] args) {
        // 1. Find the minimum cost.
        Built first = build();
        first.model().setObjective(Model.MINIMIZE, first.total());
        first.model().getSolver().setSearch(Search.inputOrderLBSearch(first.pick()));
        int best = -1;
        while (first.model().getSolver().solve()) best = first.total().getValue();
        if (best < 0) {
            System.out.println("infeasible");
            return;
        }
        if (first.model().getSolver().getSearchState() != SearchState.TERMINATED) {
            System.out.println("timeout: best found " + best + " is not proven optimal");
            return;
        }
        System.out.println("Optimal cost: " + best);

        // 2. Every choice with that cost, on a fresh model with the cost fixed.
        Built all = build();
        all.model().arithm(all.total(), "=", best).post();
        List<String> choices = new ArrayList<>();
        while (all.model().getSolver().solve()) {
            List<Integer> items = new ArrayList<>();
            for (int i = 0; i < COST.length; i++) if (all.pick()[i].getValue() == 1) items.add(i);
            choices.add("items " + items + " cost " + best);
        }
        for (String c : choices) System.out.println(c);
        System.out.println("Optimal solutions: " + choices.size());
    }
}
