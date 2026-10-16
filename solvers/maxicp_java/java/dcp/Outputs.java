package dcp;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;

import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.maxicp.cp.engine.core.CPIntVar;

/**
 * The declared outputs of a submission, by name.
 *
 * A value is a CPIntVar (a CPBoolVar reads as 0 or 1), an int, long or boolean
 * constant, or any nesting of Java arrays and Lists of these. The driver reads
 * the values of every solution from here, and forbids repeats of exactly these
 * variables when it enumerates.
 */
public final class Outputs {
    private final Map<String, Object> layout = new LinkedHashMap<>();
    private final List<CPIntVar> vars = new ArrayList<>();

    /** Declare an output. Declaring the same name twice is an error. */
    public void put(String name, Object value) {
        if (layout.containsKey(name)) throw new IllegalArgumentException("output " + name + " declared twice");
        layout.put(name, node(value, name));
    }

    /**
     * Declare a number too large for an int variable by its digits, most significant
     * first: the output is the sum of digits[i] * base^(n-1-i) as a 64-bit integer.
     */
    public void putDigits(String name, CPIntVar[] digits, int base) {
        if (layout.containsKey(name)) throw new IllegalArgumentException("output " + name + " declared twice");
        if (base < 2) throw new IllegalArgumentException("output " + name + ": base must be at least 2");
        List<Object> nodes = new ArrayList<>();
        for (CPIntVar d : digits) nodes.add(node(d, name));
        layout.put(name, new Digits(nodes, base));
    }

    boolean isEmpty() {
        return layout.isEmpty();
    }

    /** Every variable among the outputs, in declaration order (constants excluded). */
    List<CPIntVar> variables() {
        return vars;
    }

    /** The current values of variables(), in the same order. Call inside a solution callback. */
    int[] snapshot() {
        int[] values = new int[vars.size()];
        for (int i = 0; i < values.length; i++) values[i] = vars.get(i).min();
        return values;
    }

    /** The current values of every output, keyed by name. Call inside a solution callback. */
    JsonObject values() {
        JsonObject result = new JsonObject();
        for (Map.Entry<String, Object> e : layout.entrySet()) result.add(e.getKey(), read(e.getValue(), e.getKey()));
        return result;
    }

    private record Leaf(CPIntVar var) {}

    private record Digits(List<Object> digits, int base) {}

    private Object node(Object value, String name) {
        if (value instanceof CPIntVar x) {
            vars.add(x);
            return new Leaf(x);
        }
        if (value instanceof Integer || value instanceof Long || value instanceof Short || value instanceof Byte)
            return new JsonPrimitive(((Number) value).longValue());
        if (value instanceof Boolean b) return new JsonPrimitive(b);
        if (value instanceof List<?> list) {
            List<Object> nodes = new ArrayList<>();
            for (Object item : list) nodes.add(node(item, name));
            return nodes;
        }
        if (value != null && value.getClass().isArray()) {
            List<Object> nodes = new ArrayList<>();
            for (int i = 0; i < Array.getLength(value); i++) nodes.add(node(Array.get(value, i), name));
            return nodes;
        }
        throw new IllegalArgumentException("output " + name + " holds " + (value == null ? "null" : value.getClass().getName())
                + "; outputs are CPIntVar/CPBoolVar, int, long or boolean, or arrays and Lists of these");
    }

    private static JsonElement read(Object node, String name) {
        if (node instanceof Leaf leaf) {
            if (!leaf.var().isFixed())
                throw new IllegalStateException("output " + name + " is not fixed in the solution: the search must cover it");
            return new JsonPrimitive(leaf.var().min());
        }
        if (node instanceof Digits d) {
            long value = 0;
            for (Object digit : d.digits()) value = Math.addExact(Math.multiplyExact(value, d.base()), read(digit, name).getAsLong());
            return new JsonPrimitive(value);
        }
        if (node instanceof List<?> list) {
            JsonArray result = new JsonArray();
            for (Object item : list) result.add(read(item, name));
            return result;
        }
        return (JsonElement) node;
    }
}
