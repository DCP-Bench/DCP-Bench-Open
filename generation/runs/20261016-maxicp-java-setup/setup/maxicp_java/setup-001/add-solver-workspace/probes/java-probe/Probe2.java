import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.IntObjective;
import org.maxicp.search.SearchStatistics;
import org.maxicp.util.exception.InconsistencyException;
import java.util.ArrayList;
import java.util.List;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Optimisation, limits, completion flags, enumeration of optima and nogoods.
public class Probe2 {
    static DFSearch branching(CPSolver cp, CPIntVar[] vars) {
        return CPFactory.makeDfs(cp, firstFailBinary(vars));
    }

    public static void main(String[] args) {
        // A. minimise x+y with x+y >= 3 over x,y in [0,2]: optimum 3, ties (x,y) in {(1,2),(2,1)} plus (2,1)? list all
        CPSolver cp = CPFactory.makeSolver();
        CPIntVar[] v = CPFactory.makeIntVarArray(cp, 2, 3);
        CPIntVar x = v[0], y = v[1];
        CPIntVar total = CPFactory.sum(x, y);
        cp.post(ge(total, 3));
        DFSearch dfs = branching(cp, v);
        List<String> seen = new ArrayList<>();
        dfs.onSolution(() -> seen.add("(" + x.min() + "," + y.min() + ") obj=" + total.min()));
        IntObjective obj = cp.minimize(total);
        SearchStatistics st = dfs.optimize(obj);
        System.out.println("A optimize: completed=" + st.isCompleted() + " sols=" + st.numberOfSolutions() + " seen=" + seen);

        // B. same model, limit that stops early: completed must be false
        CPSolver cp2 = CPFactory.makeSolver();
        CPIntVar[] v2 = CPFactory.makeIntVarArray(cp2, 8, 6);
        CPIntVar total2 = CPFactory.sum(v2);
        cp2.post(ge(total2, 3));
        DFSearch dfs2 = branching(cp2, v2);
        SearchStatistics st2 = dfs2.optimize(cp2.minimize(total2), s -> s.numberOfNodes() > 2);
        System.out.println("B limited optimize: completed=" + st2.isCompleted() + " sols=" + st2.numberOfSolutions());

        // C. enumerate all optimal solutions: post total == optimum at root, then enumerate with nogoods
        CPSolver cp3 = CPFactory.makeSolver();
        CPIntVar[] v3 = CPFactory.makeIntVarArray(cp3, 3, 3);
        CPIntVar total3 = CPFactory.sum(v3);
        cp3.post(ge(total3, 4));
        DFSearch d3 = branching(cp3, v3);
        SearchStatistics st3 = d3.optimize(cp3.minimize(total3));
        System.out.println("C optimum completed=" + st3.isCompleted() + " sols=" + st3.numberOfSolutions());
        cp3.post(eq(total3, 4));
        int count = 0;
        List<String> sols = new ArrayList<>();
        while (true) {
            DFSearch e = branching(cp3, v3);
            StringBuilder sb = new StringBuilder();
            int[] val = new int[3];
            e.onSolution(() -> { for (int i = 0; i < 3; i++) val[i] = v3[i].min(); });
            SearchStatistics se = e.solve(s -> s.numberOfSolutions() >= 1);
            if (se.numberOfSolutions() == 0) { System.out.println("C enumeration stop: completed=" + se.isCompleted()); break; }
            sols.add("" + val[0] + val[1] + val[2]);
            List<CPBoolVar> diff = new ArrayList<>();
            for (int i = 0; i < 3; i++) diff.add(isEq(v3[i], val[i]));
            try {
                cp3.post(or(diffNot(diff)));
            } catch (InconsistencyException ex) {
                System.out.println("C nogood at root inconsistent: exhausted");
                break;
            }
            count++;
        }
        System.out.println("C optimal solutions: " + sols);

        // D. root inconsistency when posting
        CPSolver cp4 = CPFactory.makeSolver();
        CPIntVar z = CPFactory.makeIntVar(cp4, 0, 0);
        try {
            cp4.post(ge(z, 1));
            System.out.println("D no exception");
        } catch (InconsistencyException ex) {
            System.out.println("D root post raises InconsistencyException: " + ex.getClass().getName());
        }

        // E. maximise through cp.maximize
        CPSolver cp5 = CPFactory.makeSolver();
        CPIntVar[] v5 = CPFactory.makeIntVarArray(cp5, 2, 4);
        cp5.post(le(sum(v5[0], v5[1]), 5));
        DFSearch d5 = branching(cp5, v5);
        final int[] best = {-1};
        d5.onSolution(() -> best[0] = v5[0].min() + v5[1].min());
        SearchStatistics st5 = d5.optimize(cp5.maximize(sum(v5[0], v5[1])));
        System.out.println("E maximise best=" + best[0] + " completed=" + st5.isCompleted());
    }

    static CPConstraintHolder dummy;
    static class CPConstraintHolder {}

    static CPBoolVar[] diffNot(List<CPBoolVar> l) {
        CPBoolVar[] r = new CPBoolVar[l.size()];
        for (int i = 0; i < r.length; i++) r[i] = not(l.get(i));
        return r;
    }
}
