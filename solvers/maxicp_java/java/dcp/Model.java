package dcp;

import java.util.ArrayList;
import java.util.List;

import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;

/**
 * The solver a submission builds into.
 *
 * Variables created through this class are registered, and the driver branches
 * on every one of them, as it does on every output and on the objective, so a
 * solution fixes all of them and every posted constraint has been checked.
 * Variables made with CPFactory directly are not registered: they are fixed
 * only when they are outputs or the objective, and may stay unfixed otherwise.
 * Views (plus, minus, sum, element, ...) need no registration: they follow the
 * variables they are built from.
 */
public final class Model {
    private final CPSolver cp = CPFactory.makeSolver();
    private final List<CPIntVar> variables = new ArrayList<>();
    private CPIntVar objective;
    private boolean minimise;

    /** The solver, for posting constraints with CPFactory and cp.post. */
    public CPSolver cp() {
        return cp;
    }

    public CPIntVar intVar(int min, int max) {
        CPIntVar x = CPFactory.makeIntVar(cp, min, max);
        variables.add(x);
        return x;
    }

    public CPIntVar[] intVarArray(int n, int min, int max) {
        CPIntVar[] xs = new CPIntVar[n];
        for (int i = 0; i < n; i++) xs[i] = intVar(min, max);
        return xs;
    }

    public CPBoolVar boolVar() {
        CPBoolVar b = CPFactory.makeBoolVar(cp);
        variables.add(b);
        return b;
    }

    public CPBoolVar[] boolVarArray(int n) {
        CPBoolVar[] bs = new CPBoolVar[n];
        for (int i = 0; i < n; i++) bs[i] = boolVar();
        return bs;
    }

    /** Declare the objective to minimise. Once per model. */
    public void minimize(CPIntVar x) {
        setObjective(x, true);
    }

    /** Declare the objective to maximise. Once per model. */
    public void maximize(CPIntVar x) {
        setObjective(x, false);
    }

    private void setObjective(CPIntVar x, boolean minimise) {
        if (objective != null) throw new IllegalStateException("the objective is already declared");
        if (x == null) throw new IllegalArgumentException("the objective must not be null");
        objective = x;
        this.minimise = minimise;
    }

    List<CPIntVar> variables() {
        return variables;
    }

    /** The declared objective, or null for a satisfaction problem. */
    CPIntVar objective() {
        return objective;
    }

    boolean minimise() {
        return minimise;
    }
}
