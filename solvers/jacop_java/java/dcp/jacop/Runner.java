package dcp.jacop;

import java.io.FileDescriptor;
import java.io.FileOutputStream;
import java.io.PrintStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collection;
import java.util.IdentityHashMap;
import java.util.List;
import java.util.Map;

import org.jacop.constraints.Or;
import org.jacop.constraints.PrimitiveConstraint;
import org.jacop.constraints.XeqC;
import org.jacop.constraints.XneqC;
import org.jacop.constraints.XplusYeqC;
import org.jacop.core.IntVar;
import org.jacop.core.Store;
import org.jacop.core.Var;
import org.jacop.search.DepthFirstSearch;
import org.jacop.search.IndomainMin;
import org.jacop.search.SimpleSelect;
import org.jacop.search.SmallestDomain;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

/**
 * Entry point of the jacop_java image. Reads the evaluator request on stdin,
 * calls the submission's {@code Submission.build(JSONObject, Store)}, solves
 * with JaCoP's depth-first search, and writes the JSONL runner protocol on
 * stdout: zero or more {@code solution} records, then exactly one
 * {@code status}.
 *
 * <p>{@code System.out} is pointed at stderr before the submission runs, so a
 * model's prints are logs and never corrupt the protocol stream.
 */
public final class Runner {
    private static final PrintStream PROTOCOL = new PrintStream(
            new FileOutputStream(FileDescriptor.out), true, StandardCharsets.UTF_8);

    private final long started = System.nanoTime();
    private final double budget;

    private Runner(double budget) {
        this.budget = budget;
    }

    public static void main(String[] args) throws Exception {
        System.setOut(System.err);
        JSONObject request = new JSONObject(new JSONTokener(System.in));
        Runner runner = new Runner(request.getDouble("execution_timeout"));
        try {
            runner.run(request);
        } catch (Throwable error) {
            Throwable cause = error instanceof InvocationTargetException wrapped ? wrapped.getCause() : error;
            cause.printStackTrace(System.err);
            runner.status("error", String.valueOf(cause));
        }
        PROTOCOL.flush();
    }

    private double spent() {
        return (System.nanoTime() - started) / 1e9;
    }

    private double remaining() {
        return budget - spent();
    }

    private void status(String kind, String detail) {
        JSONObject record = new JSONObject();
        record.put("type", "status");
        record.put("status", kind);
        record.put("detail", detail);
        record.put("solve_seconds", spent());
        PROTOCOL.println(record);
    }

    /** The outcome of one search: whether it found a solution, and whether it ran out of time. */
    private record Outcome(boolean found, boolean timedOut, JSONObject values, int[] leafValues, int cost) {
    }

    private void run(JSONObject request) throws Exception {
        if (request.optBoolean("legacy", false)) {
            status("unsupported", "This integration has no legacy submission format");
            return;
        }
        int limit = request.optInt("solution_limit", 1);

        Store store = new Store();
        Method build = Class.forName("Submission").getDeclaredMethod("build", JSONObject.class, Store.class);
        build.setAccessible(true);
        Object returned = build.invoke(null, request.getJSONObject("instance"), store);
        if (!(returned instanceof Model model)) {
            status("error", "build must return a dcp.jacop.Model, returned "
                    + (returned == null ? "null" : returned.getClass().getName()));
            return;
        }
        if (model.outputs.isEmpty()) {
            status("error", "the model declared no outputs");
            return;
        }
        JSONArray declared = request.optJSONArray("outputs");
        if (declared != null) {
            for (int i = 0; i < declared.length(); i++) {
                if (!model.outputs.containsKey(declared.getString(i))) {
                    System.err.println("warning: output " + declared.getString(i) + " is declared by the problem"
                            + " but not by the model");
                }
            }
        }

        // The cost JaCoP minimises. A maximised objective is minimised through
        // its negation, a variable added before the search variables are
        // collected so that it is labelled like every other.
        IntVar cost = model.objective;
        if (cost != null && model.maximize) {
            cost = new IntVar(store, "dcp_negated_objective", -model.objective.max(), -model.objective.min());
            store.impose(new XplusYeqC(model.objective, cost, 0));
        }

        IntVar[] variables = searchVariables(store, model);
        List<IntVar> leaves = model.leaves();
        int base = store.level;
        int emitted = 0;
        // Propagate once at the base level before any search. JaCoP drops a
        // constraint that is first found satisfied inside a search level and
        // does not restore it when that level is removed, so every constraint
        // has to have been propagated here before the store is searched twice.
        if (!store.consistency()) {
            status("unsat", "");
            return;
        }

        if (cost != null) {
            Outcome optimum = solve(store, model, variables, leaves, cost, base);
            if (!optimum.found()) {
                status(optimum.timedOut() ? "timeout" : "unsat", "");
                return;
            }
            // A solution found but not proven optimal is never reported: that
            // would claim an optimum JaCoP did not establish.
            if (optimum.timedOut()) {
                status("timeout", "the optimum was not proven");
                return;
            }
            PROTOCOL.println(new JSONObject().put("type", "solution").put("values", optimum.values()));
            emitted = 1;
            if (emitted >= limit) {
                status("limit", "");
                return;
            }
            store.impose(new XeqC(cost, optimum.cost()));
            if (!block(store, leaves, optimum.leafValues())) {
                status("complete", "");
                return;
            }
        }

        while (emitted < limit) {
            if (remaining() <= 0) {
                status("timeout", "");
                return;
            }
            Outcome next = solve(store, model, variables, leaves, null, base);
            if (!next.found()) {
                // Exhausted: every remaining assignment repeats output values
                // already emitted.
                status(next.timedOut() ? "timeout" : emitted > 0 ? "complete" : "unsat", "");
                return;
            }
            PROTOCOL.println(new JSONObject().put("type", "solution").put("values", next.values()));
            emitted++;
            if (emitted < limit && !block(store, leaves, next.leafValues())) {
                status("complete", "");
                return;
            }
        }
        status("limit", "");
    }

    /**
     * Searches one level above {@code base} so that the assignment JaCoP leaves
     * behind can be read and then undone, keeping the store reusable for the
     * next search.
     */
    private Outcome solve(Store store, Model model, IntVar[] variables, List<IntVar> leaves, IntVar cost, int base) {
        store.setLevel(base + 1);
        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setTimeOutMilliseconds(Math.max(1, (long) (remaining() * 1000)));
        SimpleSelect<IntVar> select = new SimpleSelect<>(variables,
                model.order == null ? new SmallestDomain<>() : model.comparator,
                model.indomain == null ? new IndomainMin<>() : model.indomain);
        boolean found = cost == null ? search.labeling(store, select) : search.labeling(store, select, cost);
        Outcome outcome;
        if (found) {
            JSONObject values = new JSONObject();
            for (Map.Entry<String, Object> entry : model.outputs.entrySet()) {
                values.put(entry.getKey(), render(entry.getValue()));
            }
            int[] leafValues = new int[leaves.size()];
            for (int i = 0; i < leafValues.length; i++) {
                leafValues[i] = leaves.get(i).value();
            }
            outcome = new Outcome(true, search.timeOutOccured, values, leafValues, cost == null ? 0 : cost.value());
        } else {
            outcome = new Outcome(false, search.timeOutOccured, null, null, 0);
        }
        store.removeLevel(base + 1);
        store.setLevel(base);
        return outcome;
    }

    /**
     * Rules out the output values just emitted. False when no other output
     * values remain possible: nothing left to vary, or propagation fails.
     */
    private static boolean block(Store store, List<IntVar> leaves, int[] values) {
        List<PrimitiveConstraint> differ = new ArrayList<>();
        for (int i = 0; i < values.length; i++) {
            if (!leaves.get(i).singleton()) {
                differ.add(new XneqC(leaves.get(i), values[i]));
            }
        }
        if (differ.isEmpty()) {
            return false;
        }
        store.impose(new Or(differ.toArray(new PrimitiveConstraint[0])));
        // Propagated here, at the base level, for the reason given in run().
        return store.consistency();
    }

    /**
     * The model's own search order first, then its outputs, then every other
     * integer variable in the store, so a solution never leaves a variable
     * unfixed whatever the model chose to label.
     */
    private static IntVar[] searchVariables(Store store, Model model) {
        Map<IntVar, Boolean> seen = new IdentityHashMap<>();
        List<IntVar> ordered = new ArrayList<>();
        if (model.order != null) {
            for (IntVar v : model.order) {
                if (v != null && seen.put(v, true) == null) {
                    ordered.add(v);
                }
            }
        }
        for (IntVar v : model.leaves()) {
            if (seen.put(v, true) == null) {
                ordered.add(v);
            }
        }
        for (int i = 0; i < store.size(); i++) {
            Var v = store.vars[i];
            if (v instanceof IntVar iv && seen.put(iv, true) == null) {
                ordered.add(iv);
            }
        }
        return ordered.toArray(new IntVar[0]);
    }

    private static Object render(Object value) {
        if (value instanceof IntVar v) {
            return v.value();
        }
        if (value instanceof Integer || value instanceof Boolean) {
            return value;
        }
        JSONArray array = new JSONArray();
        if (value instanceof int[] ints) {
            for (int item : ints) {
                array.put(item);
            }
        } else if (value instanceof boolean[] flags) {
            for (boolean item : flags) {
                array.put(item);
            }
        } else if (value instanceof Object[] items) {
            for (Object item : items) {
                array.put(render(item));
            }
        } else if (value instanceof Collection<?> items) {
            for (Object item : items) {
                array.put(render(item));
            }
        } else {
            throw new IllegalStateException("unsupported output value " + value);
        }
        return array;
    }
}
