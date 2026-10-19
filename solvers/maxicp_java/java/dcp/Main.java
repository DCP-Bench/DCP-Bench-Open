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
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Predicate;
import java.util.function.Supplier;

import org.maxicp.cp.CPFactory;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.IntObjective;
import org.maxicp.search.SearchStatistics;
import org.maxicp.search.Searches;
import org.maxicp.util.exception.InconsistencyException;

/**
 * Driver for MaxiCP submissions.
 *
 * A submission is one Java file declaring
 * {@code public class Submission { public static void build(Instance inst, Model model, Outputs out) }}.
 * It posts constraints on the Model's solver, declares its outputs and, for an
 * optimisation problem, the objective. This driver owns the search, the
 * optimum proof, the enumeration and the runner protocol: one "solution" line
 * per solution, then one "status" line on stdout. Anything the submission
 * prints goes to stderr.
 *
 * A search counts as exhausted only when MaxiCP reports it completed; one
 * stopped by the deadline is reported as a timeout.
 */
public final class Main {
    private static final Gson GSON = new Gson();
    private static PrintStream protocol;
    private static long started;

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
        Predicate<SearchStatistics> timeUp = stats -> System.nanoTime() >= deadline;

        Model model = new Model();
        Outputs out = new Outputs();
        try {
            build(new Instance(request.getAsJsonObject("instance")), model, out);
        } catch (InvocationTargetException error) {
            // A constraint refuted at the root while the model was built: no solution.
            if (error.getCause() instanceof InconsistencyException) {
                status("unsat", "");
                return;
            }
            throw error;
        }
        if (out.isEmpty()) throw new IllegalStateException("Expected output dictionary: declare at least one output with out.put");

        CPSolver cp = model.cp();
        // MaxiCP 0.0.3 overflows its objective bound on offset views (CPIntVarViewOffset
        // computes v - o with the bound at 2147483646), so optimise a fresh variable that
        // equals the declared objective. Its domain is the objective's root domain.
        CPIntVar declared = model.objective();
        CPIntVar objective = declared == null ? null : freshObjective(cp, declared);
        // Branch on every variable the submission made, on every output and on the
        // objective, so a solution fixes all of them and every constraint has been checked.
        Set<CPIntVar> decisions = new LinkedHashSet<>(model.variables());
        decisions.addAll(out.variables());
        if (declared != null) {
            decisions.add(declared);
            decisions.add(objective);
        }
        Supplier<Runnable[]> branching = Searches.firstFailBinary(decisions.toArray(new CPIntVar[0]));

        List<JsonObject> found = new ArrayList<>();
        Outcome outcome;
        if (declared == null) {
            outcome = enumerate(cp, branching, out, limit, timeUp, found);
        } else {
            IntObjective bound = model.minimise() ? cp.minimize(objective) : cp.maximize(objective);
            DFSearch search = CPFactory.makeDfs(cp, branching);
            long[] bestValue = {0};
            search.onSolution(() -> bestValue[0] = objective.min());
            SearchStatistics stats = search.optimize(bound, timeUp);
            if (!stats.isCompleted()) {
                status("timeout", "Candidate optimum was not proven");
                return;
            }
            if (stats.numberOfSolutions() == 0) {
                status("unsat", "");
                return;
            }
            // The optimum is proven. Fix it at the root and enumerate the optima.
            cp.post(CPFactory.eq(objective, (int) bestValue[0]));
            outcome = enumerate(cp, branching, out, limit, timeUp, found);
        }
        finish(outcome, found);
    }

    // A plain variable with the declared objective's root domain, posted equal to it.
    private static CPIntVar freshObjective(CPSolver cp, CPIntVar declared) {
        CPIntVar target = CPFactory.makeIntVar(cp, declared.min(), declared.max());
        cp.post(CPFactory.eq(target, declared));
        return target;
    }

    /**
     * Enumerate solutions that differ in a declared output, until the limit, the
     * end of the search or the deadline. Each solution is followed by a no-good on
     * the output values, so auxiliary variables cannot repeat an output.
     */
    private static Outcome enumerate(CPSolver cp, Supplier<Runnable[]> branching, Outputs out, int limit,
                                     Predicate<SearchStatistics> timeUp, List<JsonObject> found) {
        while (found.size() < limit) {
            JsonObject[] values = {null};
            int[][] snapshot = {null};
            DFSearch search = CPFactory.makeDfs(cp, branching);
            search.onSolution(() -> {
                values[0] = out.values();
                snapshot[0] = out.snapshot();
            });
            SearchStatistics stats = search.solve(s -> s.numberOfSolutions() >= 1 || timeUp.test(s));
            if (values[0] == null) return stats.isCompleted() ? Outcome.EXHAUSTED : Outcome.TIMEOUT;
            found.add(values[0]);
            if (found.size() >= limit) return Outcome.LIMIT;
            if (out.variables().isEmpty()) return Outcome.EXHAUSTED;
            try {
                forbid(cp, out.variables(), snapshot[0]);
            } catch (InconsistencyException refuted) {
                // The last distinct solution is found: nothing is left to forbid.
                return Outcome.EXHAUSTED;
            }
        }
        return Outcome.LIMIT;
    }

    // At least one output variable differs from its value in the solution.
    private static void forbid(CPSolver cp, List<CPIntVar> vars, int[] values) {
        CPBoolVar[] differ = new CPBoolVar[vars.size()];
        for (int i = 0; i < differ.length; i++) differ[i] = CPFactory.not(CPFactory.isEq(vars.get(i), values[i]));
        cp.post(CPFactory.or(differ));
    }

    private static void build(Instance inst, Model model, Outputs out) throws Exception {
        Class<?> submission;
        try {
            submission = Class.forName("Submission");
        } catch (ClassNotFoundException error) {
            throw new IllegalStateException("the submission must declare public class Submission");
        }
        Method build;
        try {
            build = submission.getMethod("build", Instance.class, Model.class, Outputs.class);
        } catch (NoSuchMethodException error) {
            throw new IllegalStateException("Submission must declare public static void build(Instance inst, Model model, Outputs out)");
        }
        if (!Modifier.isStatic(build.getModifiers())) throw new IllegalStateException("Submission.build must be static");
        build.invoke(null, inst, model, out);
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
