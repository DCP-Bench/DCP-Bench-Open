package dcp.jacop;

import java.util.ArrayList;
import java.util.Collection;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.jacop.core.IntVar;
import org.jacop.search.ComparatorVariable;
import org.jacop.search.Indomain;

/**
 * What a submission returns from {@code build}: the declared outputs, an
 * optional objective, and an optional search strategy.
 *
 * <p>This class wraps no part of JaCoP's modelling API. Variables and
 * constraints are created on the {@code org.jacop.core.Store} the submission is
 * handed, with JaCoP's own classes. What lives here has no JaCoP equivalent:
 * naming the outputs the evaluator reads, and saying which variable to
 * optimise.
 */
public final class Model {
    final Map<String, Object> outputs = new LinkedHashMap<>();
    IntVar objective;
    boolean maximize;
    IntVar[] order;
    ComparatorVariable<IntVar> comparator;
    Indomain<IntVar> indomain;

    /**
     * Declares one output under the name the problem gives it. A value is an
     * {@code IntVar} (a {@code BooleanVar} is one), an {@code int}, an
     * {@code Integer}, a {@code Boolean}, or an array or {@code Collection} of
     * those, nested to any depth.
     */
    public Model put(String name, Object value) {
        if (outputs.containsKey(name)) {
            throw new IllegalArgumentException("output " + name + " was declared twice");
        }
        check(name, value);
        outputs.put(name, value);
        return this;
    }

    /** Minimises {@code objective}. Success is reported only once JaCoP has proven the optimum. */
    public Model minimize(IntVar objective) {
        this.objective = objective;
        this.maximize = false;
        return this;
    }

    /** Maximises {@code objective}, under the same proof requirement as {@link #minimize}. */
    public Model maximize(IntVar objective) {
        this.objective = objective;
        this.maximize = true;
        return this;
    }

    /**
     * Labels {@code order} first, choosing among them with {@code comparator}
     * (null: input order) and trying values with {@code indomain} (null:
     * {@code IndomainMin}). Every other integer variable in the store is still
     * labelled after them, so a solution never leaves a variable unfixed.
     */
    public Model search(IntVar[] order, ComparatorVariable<IntVar> comparator, Indomain<IntVar> indomain) {
        this.order = order;
        this.comparator = comparator;
        this.indomain = indomain;
        return this;
    }

    private static void check(String path, Object value) {
        if (value instanceof IntVar || value instanceof Integer || value instanceof Boolean) {
            return;
        }
        if (value instanceof int[] || value instanceof boolean[]) {
            return;
        }
        if (value instanceof Object[] array) {
            for (int i = 0; i < array.length; i++) {
                check(path + "[" + i + "]", array[i]);
            }
            return;
        }
        if (value instanceof Collection<?> items) {
            int i = 0;
            for (Object item : items) {
                check(path + "[" + i++ + "]", item);
            }
            return;
        }
        throw new IllegalArgumentException("output " + path + ": unsupported value "
                + (value == null ? "null" : value.getClass().getName()));
    }

    /** Every variable in the outputs, in declaration order. */
    List<IntVar> leaves() {
        List<IntVar> out = new ArrayList<>();
        for (Object value : outputs.values()) {
            walk(value, out);
        }
        return out;
    }

    private static void walk(Object value, List<IntVar> out) {
        if (value instanceof IntVar v) {
            out.add(v);
        } else if (value instanceof Object[] array) {
            for (Object item : array) {
                walk(item, out);
            }
        } else if (value instanceof Collection<?> items) {
            for (Object item : items) {
                walk(item, out);
            }
        }
    }
}
