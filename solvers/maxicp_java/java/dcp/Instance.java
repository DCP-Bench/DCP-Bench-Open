package dcp;

import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;
import com.google.gson.JsonPrimitive;

/**
 * The instance data of one evaluation request, read with typed getters.
 *
 * Every getter throws an IllegalArgumentException naming the field when the
 * field is missing or has another shape, so a model that misreads its data
 * fails with a message rather than with a NullPointerException. JSON Booleans
 * read as 0/1 wherever an integer is asked for. Lists of lists may be ragged.
 */
public final class Instance {
    private final JsonObject data;

    Instance(JsonObject data) {
        this.data = data;
    }

    /** Whether the instance has this field. */
    public boolean has(String key) {
        return data.has(key) && !data.get(key).isJsonNull();
    }

    /** The field as Gson parsed it, for shapes the getters below do not cover. */
    public JsonElement raw(String key) {
        return field(key);
    }

    public int getInt(String key) {
        return toInt(field(key), key);
    }

    public long getLong(String key) {
        return toLong(field(key), key);
    }

    public boolean getBool(String key) {
        JsonElement e = field(key);
        if (e.isJsonPrimitive() && e.getAsJsonPrimitive().isBoolean()) return e.getAsBoolean();
        long v = toLong(e, key);
        if (v == 0 || v == 1) return v == 1;
        throw new IllegalArgumentException("field " + key + " is not a Boolean: " + e);
    }

    public double getDouble(String key) {
        JsonElement e = field(key);
        if (!e.isJsonPrimitive() || !e.getAsJsonPrimitive().isNumber())
            throw new IllegalArgumentException("field " + key + " is not a number: " + e);
        return e.getAsDouble();
    }

    public String getString(String key) {
        JsonElement e = field(key);
        if (!e.isJsonPrimitive() || !e.getAsJsonPrimitive().isString())
            throw new IllegalArgumentException("field " + key + " is not a string: " + e);
        return e.getAsString();
    }

    public int[] getIntArray(String key) {
        return ints(list(field(key), key), key);
    }

    public long[] getLongArray(String key) {
        JsonArray a = list(field(key), key);
        long[] r = new long[a.size()];
        for (int i = 0; i < r.length; i++) r[i] = toLong(a.get(i), key);
        return r;
    }

    public boolean[] getBoolArray(String key) {
        int[] v = getIntArray(key);
        boolean[] r = new boolean[v.length];
        for (int i = 0; i < v.length; i++) {
            if (v[i] != 0 && v[i] != 1) throw new IllegalArgumentException("field " + key + " is not a list of Booleans");
            r[i] = v[i] == 1;
        }
        return r;
    }

    /** A list of lists of integers; rows may differ in length. */
    public int[][] getIntMatrix(String key) {
        JsonArray a = list(field(key), key);
        int[][] r = new int[a.size()][];
        for (int i = 0; i < r.length; i++) r[i] = ints(list(a.get(i), key), key);
        return r;
    }

    /** Three nested lists of integers; any level may be ragged. */
    public int[][][] getInt3(String key) {
        JsonArray a = list(field(key), key);
        int[][][] r = new int[a.size()][][];
        for (int i = 0; i < r.length; i++) {
            JsonArray b = list(a.get(i), key);
            r[i] = new int[b.size()][];
            for (int j = 0; j < r[i].length; j++) r[i][j] = ints(list(b.get(j), key), key);
        }
        return r;
    }

    public String[] getStringArray(String key) {
        JsonArray a = list(field(key), key);
        String[] r = new String[a.size()];
        for (int i = 0; i < r.length; i++) {
            JsonElement e = a.get(i);
            if (!e.isJsonPrimitive() || !e.getAsJsonPrimitive().isString())
                throw new IllegalArgumentException("field " + key + " is not a list of strings");
            r[i] = e.getAsString();
        }
        return r;
    }

    private JsonElement field(String key) {
        if (!has(key)) throw new IllegalArgumentException("instance has no field " + key);
        return data.get(key);
    }

    private static JsonArray list(JsonElement e, String key) {
        if (!e.isJsonArray()) throw new IllegalArgumentException("field " + key + " is not a list where one was expected: " + e);
        return e.getAsJsonArray();
    }

    private static int[] ints(JsonArray a, String key) {
        int[] r = new int[a.size()];
        for (int i = 0; i < r.length; i++) r[i] = toInt(a.get(i), key);
        return r;
    }

    private static long toLong(JsonElement e, String key) {
        if (e.isJsonPrimitive()) {
            JsonPrimitive p = e.getAsJsonPrimitive();
            if (p.isBoolean()) return p.getAsBoolean() ? 1 : 0;
            if (p.isNumber()) {
                try {
                    return p.getAsBigDecimal().longValueExact();
                } catch (ArithmeticException error) {
                    throw new IllegalArgumentException("field " + key + " holds a value that is not a 64-bit integer: " + e);
                }
            }
        }
        throw new IllegalArgumentException("field " + key + " is not an integer where one was expected: " + e);
    }

    private static int toInt(JsonElement e, String key) {
        long v = toLong(e, key);
        if (v < Integer.MIN_VALUE || v > Integer.MAX_VALUE)
            throw new IllegalArgumentException("field " + key + " holds " + v + ", outside the int range; use getLong");
        return (int) v;
    }
}
