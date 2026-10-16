package dcp;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

import java.io.InputStreamReader;
import java.io.PrintStream;
import java.lang.management.ManagementFactory;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.ResolutionPolicy;
import org.chocosolver.solver.SettingsBuilder;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.constraints.Constraint;
import org.chocosolver.solver.search.SearchState;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.variables.Variable;

/**
 * Driver for Choco submissions.
 *
 * A submission is one Java file declaring
 * {@code public class Submission { public static void build(Instance inst, Model model, Outputs out) }}.
 * It posts its constraints on the Choco Model it is handed, declares its
 * outputs, and sets an objective with {@code model.setObjective(...)} when the
 * problem has one. It may also declare
 * {@code public static SettingsBuilder settings()}, whose result the driver
 * passes to the Model it creates (for example to turn on LCG). This driver reads the request on stdin, solves, and writes
 * the runner protocol on stdout: one "solution" line per solution, then one
 * "status" line. Anything the submission prints goes to stderr.
 *
 * A search counts as exhausted only when Choco ends it in the TERMINATED state;
 * one ended by the deadline is STOPPED, and is reported as a timeout.
 */
public final class Main {
    private static final Gson GSON = new Gson();
    private static PrintStream protocol;
    private static long started;

    private record Built(Model model, Outputs outputs) {}

    private enum Outcome { LIMIT, EXHAUSTED, TIMEOUT }

    public static void main(String[] args) {
        started = System.nanoTime();
        protocol = System.out;
        System.setOut(System.err);
        try {
            JsonObject request = JsonParser.parseReader(new InputStreamReader(System.in, StandardCharsets.UTF_8)).getAsJsonObject();
            run(request);
        } catch (Throwable error) {
            Throwable cause = error instanceof InvocationTargetException ? error.getCause() : error;
            cause.printStackTrace(System.err);
            status("error", describe(cause));
        }
        protocol.flush();
        System.exit(0);
    }

    private static void run(JsonObject request) throws Exception {
        double budget = request.get("execution_timeout").getAsDouble();
        int limit = request.get("solution_limit").getAsInt();
        if (limit < 1) throw new IllegalArgumentException("solution_limit must be positive");
        // The budget counts from the start of the JVM; finish a little before
        // the runner's own timer so the status is ours.
        long jvmAgeNanos = (System.currentTimeMillis() - ManagementFactory.getRuntimeMXBean().getStartTime()) * 1_000_000L;
        long deadline = started - jvmAgeNanos + (long) (Math.max(0.1, budget - 0.5) * 1e9);
        JsonObject data = request.getAsJsonObject("instance");
        Class<?> submission = submission();
        Method build = entrypoint(submission);
        Method settings = settings(submission);

        Factory factory = () -> build(build, settings, data);
        Built built = factory.make();
        Model model = built.model();
        List<JsonObject> found = new ArrayList<>();
        List<int[]> forbidden = new ArrayList<>();

        if (model.getResolutionPolicy() != ResolutionPolicy.SATISFACTION) {
            Variable objective = model.getObjective();
            if (!(objective instanceof IntVar)) throw new IllegalStateException("the objective must be an IntVar");
            IntVar obj = (IntVar) objective;
            Solver solver = model.getSolver();
            solver.addStopCriterion(() -> System.nanoTime() >= deadline);
            Integer best = null;
            JsonObject bestValues = null;
            int[] bestVars = null;
            // Each solve() returns a strictly better solution; the last one is
            // optimal when the search then ends without a stop.
            while (solver.solve()) {
                best = obj.getValue();
                bestValues = built.outputs().values();
                bestVars = built.outputs().snapshot();
            }
            if (solver.getSearchState() == SearchState.STOPPED) {
                status("timeout", best == null ? "" : "Candidate optimum was not proven");
                return;
            }
            if (best == null) {
                status("unsat", "");
                return;
            }
            found.add(bestValues);
            forbidden.add(bestVars);
            if (limit == 1) {
                finish(Outcome.LIMIT, found);
                return;
            }
            // Enumerate the other optima on fresh models with the objective
            // fixed; the optimum already found is forbidden like any other.
            int optimum = best;
            factory = () -> {
                Built fresh = build(build, settings, data);
                IntVar fixed = (IntVar) fresh.model().getObjective();
                fresh.model().clearObjective();
                fresh.model().arithm(fixed, "=", optimum).post();
                return fresh;
            };
            built = null;
        }
        finish(enumerate(factory, built, limit, deadline, found, forbidden), found);
    }

    private interface Factory {
        Built make() throws Exception;
    }

    /**
     * Collect solutions that differ on the declared outputs, until there are
     * `limit` of them or the search is exhausted. After each solution the
     * search starts again from the root with a no-good on the declared
     * outputs, so a free variable outside the outputs cannot produce repeats.
     * The no-good is posted on the same model after a reset, except under
     * lazy clause generation, where Choco 6.0.1 fails on constraints posted
     * after a reset: there every step solves a fresh model with all no-goods.
     */
    private static Outcome enumerate(Factory factory, Built built, int limit, long deadline,
                                     List<JsonObject> found, List<int[]> forbidden) throws Exception {
        while (found.size() < limit) {
            if (System.nanoTime() >= deadline) return Outcome.TIMEOUT;
            if (built == null || built.model().getSolver().isLCG()) {
                built = factory.make();
                if (!forbidden.isEmpty() && built.outputs().variables().isEmpty()) return Outcome.EXHAUSTED;
                for (int[] values : forbidden) post(built.model(), built.outputs().variables(), values);
            }
            Solver solver = built.model().getSolver();
            solver.addStopCriterion(() -> System.nanoTime() >= deadline);
            boolean solved = solver.solve();
            if (!solved) return solver.getSearchState() == SearchState.STOPPED ? Outcome.TIMEOUT : Outcome.EXHAUSTED;
            found.add(built.outputs().values());
            int[] current = built.outputs().snapshot();
            forbidden.add(current);
            if (built.outputs().variables().isEmpty()) return found.size() >= limit ? Outcome.LIMIT : Outcome.EXHAUSTED;
            if (!solver.isLCG()) {
                solver.reset();
                post(built.model(), built.outputs().variables(), current);
            }
        }
        return Outcome.LIMIT;
    }

    // At least one output variable differs from its value in this solution.
    private static void post(Model model, List<IntVar> vars, int[] values) {
        Constraint[] differ = new Constraint[vars.size()];
        for (int i = 0; i < differ.length; i++) differ[i] = model.arithm(vars.get(i), "!=", values[i]);
        if (differ.length == 1) differ[0].post();
        else model.or(differ).post();
    }

    private static Class<?> submission() {
        try {
            return Class.forName("Submission");
        } catch (ClassNotFoundException error) {
            throw new IllegalStateException("the submission must declare public class Submission");
        }
    }

    private static Method settings(Class<?> submission) {
        Method settings;
        try {
            settings = submission.getMethod("settings");
        } catch (NoSuchMethodException error) {
            return null;
        }
        if (!Modifier.isStatic(settings.getModifiers()) || !SettingsBuilder.class.isAssignableFrom(settings.getReturnType()))
            throw new IllegalStateException("Submission.settings must be public static SettingsBuilder settings()");
        return settings;
    }

    private static Method entrypoint(Class<?> submission) {
        Method build;
        try {
            build = submission.getMethod("build", Instance.class, Model.class, Outputs.class);
        } catch (NoSuchMethodException error) {
            throw new IllegalStateException("Submission must declare public static void build(Instance inst, Model model, Outputs out)");
        }
        if (!Modifier.isStatic(build.getModifiers()))
            throw new IllegalStateException("Submission.build must be static");
        return build;
    }

    private static Built build(Method build, Method settings, JsonObject data) throws Exception {
        Model model = settings == null ? new Model("submission")
                : new Model("submission", (SettingsBuilder) settings.invoke(null));
        Outputs outputs = new Outputs();
        build.invoke(null, new Instance(data), model, outputs);
        // A search the model declares over some variables is extended over
        // all of them, so every output is fixed in a solution.
        model.getSolver().makeCompleteStrategy(true);
        if (outputs.isEmpty()) throw new IllegalStateException("Expected output dictionary: declare at least one output with out.put");
        return new Built(model, outputs);
    }

    private static void finish(Outcome outcome, List<JsonObject> found) {
        for (JsonObject values : found) {
            Map<String, Object> record = new LinkedHashMap<>();
            record.put("type", "solution");
            record.put("values", values);
            protocol.println(GSON.toJson(record));
        }
        switch (outcome) {
            case LIMIT -> status("limit", "");
            case TIMEOUT -> status("timeout", "");
            case EXHAUSTED -> status(found.isEmpty() ? "unsat" : "complete", "");
        }
    }

    private static void status(String status, String detail) {
        Map<String, Object> record = new LinkedHashMap<>();
        record.put("type", "status");
        record.put("status", status);
        record.put("solve_seconds", (System.nanoTime() - started) / 1e9);
        record.put("detail", detail);
        protocol.println(GSON.toJson(record));
        protocol.flush();
    }

    private static String describe(Throwable error) {
        StringBuilder text = new StringBuilder(error.toString());
        StackTraceElement[] trace = error.getStackTrace();
        for (int i = 0; i < Math.min(3, trace.length); i++) text.append("\n  at ").append(trace[i]);
        return text.toString();
    }
}
