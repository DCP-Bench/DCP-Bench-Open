// Checks the semantics of Choco 6.0.1 constraints against brute force.
// Each check posts a constraint on v (ints in [lo, hi]), counts the solutions,
// and compares with a brute-force count of a predicate over the same vectors.
// Every check runs twice: with the default settings and with LCG on.
// Build and run (Java 17+):
//   javac -cp choco-solver-6.0.1-jar-with-dependencies.jar -d out catalogue.java
//   java -cp out:choco-solver-6.0.1-jar-with-dependencies.jar Catalogue
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.function.BiConsumer;
import java.util.function.Predicate;

import org.chocosolver.solver.Model;
import org.chocosolver.solver.Settings;
import org.chocosolver.solver.SettingsBuilder;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.constraints.extension.Tuples;
import org.chocosolver.solver.constraints.nary.automata.FA.FiniteAutomaton;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import org.chocosolver.solver.variables.SetVar;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.variables.Task;

public class Catalogue {
    static int failures = 0;
    static final List<String> lcgUnsupported = new ArrayList<>();

    static IntVar[] slice(IntVar[] v, int from, int to) {
        return Arrays.copyOfRange(v, from, to);
    }

    static BoolVar[] bools(Model m, IntVar[] v) {
        BoolVar[] b = new BoolVar[v.length];
        for (int i = 0; i < v.length; i++) b[i] = m.boolVar();
        for (int i = 0; i < v.length; i++) m.arithm(b[i], "=", v[i]).post();
        return b;
    }

    static long solve(int n, int lo, int hi, boolean lcg, BiConsumer<Model, IntVar[]> post) {
        Model m = lcg ? new Model("check", SettingsBuilder.init().setLCG(true)) : new Model("check");
        IntVar[] v = m.intVarArray("v", n, lo, hi);
        post.accept(m, v);
        Solver s = m.getSolver();
        // Count distinct assignments of v only: auxiliaries made inside the
        // check are functionally determined in every check below.
        java.util.Set<String> seen = new java.util.HashSet<>();
        s.setSearch(org.chocosolver.solver.search.strategy.Search.inputOrderLBSearch(v));
        s.makeCompleteStrategy(true);
        while (s.solve()) {
            int[] a = new int[n];
            for (int i = 0; i < n; i++) a[i] = v[i].getValue();
            seen.add(Arrays.toString(a));
        }
        return seen.size();
    }

    static long brute(int n, int lo, int hi, Predicate<int[]> p) {
        int[] a = new int[n];
        Arrays.fill(a, lo);
        long count = 0;
        while (true) {
            if (p.test(a)) count++;
            int i = 0;
            while (i < n && a[i] == hi) a[i++] = lo;
            if (i == n) return count;
            a[i]++;
        }
    }

    static void check(String name, int n, int lo, int hi, BiConsumer<Model, IntVar[]> post, Predicate<int[]> p) {
        long expected = brute(n, lo, hi, p);
        long got = solve(n, lo, hi, false, post);
        String lcg;
        try {
            long withLcg = solve(n, lo, hi, true, post);
            lcg = withLcg == expected ? "lcg ok" : "LCG WRONG " + withLcg;
            if (withLcg != expected) lcgUnsupported.add(name + " (wrong count)");
        } catch (Throwable error) {
            lcg = "lcg unsupported: " + error.getClass().getSimpleName();
            lcgUnsupported.add(name + " (" + error.getClass().getSimpleName() + ")");
        }
        boolean ok = got == expected;
        if (!ok) failures++;
        System.out.printf("%-4s %-40s choco=%d brute=%d  %s%n", ok ? "ok" : "FAIL", name, got, expected, lcg);
    }

    static boolean distinct(int[] a, int from, int to) {
        for (int i = from; i < to; i++) for (int j = i + 1; j < to; j++) if (a[i] == a[j]) return false;
        return true;
    }

    static int occurrences(int[] a, int from, int to, int value) {
        int c = 0;
        for (int i = from; i < to; i++) if (a[i] == value) c++;
        return c;
    }

    static long nvalues(int[] a, int from, int to) {
        return Arrays.stream(a, from, to).distinct().count();
    }

    // succ[i] = a[from + i] - offset; true when the successors form one
    // circuit through all nodes.
    static boolean circuit(int[] a, int from, int n, int offset) {
        int node = 0;
        boolean[] seen = new boolean[n];
        for (int step = 0; step < n; step++) {
            if (seen[node]) return false;
            seen[node] = true;
            int next = a[from + node] - offset;
            if (next < 0 || next >= n) return false;
            node = next;
        }
        return node == 0;
    }


    // Compiled, never run: every call named in constraints.md and SKILL.md
    // that the checks above do not use, so a wrong name or argument order
    // fails the build.
    @SuppressWarnings("unused")
    static void signatures() {
        Model m = new Model("signatures", SettingsBuilder.init().setLCG(false));
        IntVar x = m.intVar("x", 0, 9), y = m.intVar("y", 0, 9), z = m.intVar("z", 0, 9, true);
        IntVar[] xs = m.intVarArray("xs", 4, 0, 9);
        IntVar[] ys = m.intVarArray("ys", 4, new int[]{1, 3, 5});
        IntVar[][] grid = m.intVarMatrix("grid", 3, 3, 0, 9);
        IntVar w = m.intVar("w", new int[]{1, 4, 9});
        BoolVar b = m.boolVar("b");
        BoolVar[] bs = m.boolVarArray("bs", 4);
        BoolVar[][] bm = m.boolVarMatrix("bm", 2, 2);
        BoolVar[] cast = m.toBoolVar(m.intVar(0, 1));
        SetVar s = m.setVar("s", new int[]{}, new int[]{0, 1, 2, 3});
        SetVar[] ss = m.setVarArray("ss", 2, new int[]{}, new int[]{0, 1, 2, 3});
        Task t = m.taskVar(x, 3);
        Task t2 = m.taskVar(y, m.intVar(1, 3), m.intVar(0, 20));
        Task opt = m.taskVar(x, 2, b);

        IntVar v1 = m.offset(x, 2), v2 = m.mul(x, 3), v3 = m.neg(x), v4 = m.abs(x), v5 = m.intView(2, x, 1);
        BoolVar e1 = m.isEq(x, 3), e2 = m.isNeq(x, 3), e3 = m.isLeq(x, 3), e4 = m.isGeq(x, 3), e5 = m.boolNotView(b), e6 = b.not();
        BoolVar sv = m.setBoolView(s, 2);
        BoolVar[] svs = m.setBoolsView(s, 4, 0);
        SetVar bsv = m.boolsSetView(bs, 0);
        SetVar isv = m.intsSetView(xs, 3, 0);

        m.arithm(x, "*", y, "=", 12).post();
        m.arithm(x, "/", y, "<=", z).post();
        m.times(x, 3, z).post();
        m.times(x, y, 6).post();
        m.mod(x, 3, 1).post();
        m.pow(x, y, z).post();
        m.distance(x, y, "<=", z).post();
        m.max(z, x, y).post();
        m.min(z, x, y).post();
        m.member(x, 2, 5).post();
        m.notMember(x, new int[]{1, 2}).post();

        IntVar fromExpr = x.add(y).mul(2).sub(z).intVar();
        BoolVar fromRel = x.lt(y).and(y.ne(3)).xor(z.in(1, 2)).iff(b).boolVar();
        x.add(y, z).le(10).post();
        x.mul(y, z).ge(0).post();
        x.min(y, z).eq(w).post();
        x.max(y).notin(0, 9).post();
        x.mod(3).sqr().pow(2).neg().lt(0).not().post();
        x.ge(y).imp(z.eq(0)).decompose().post();
        x.add(y).eq(z).extension().post();
        x.eq(y.eq(0).ift(1, 2)).post();

        m.sum(xs, "<=", 20).post();
        m.sum(xs, "=", ys).post();
        m.sum(bs, "=", x).post();
        IntVar total = m.sum("total", xs);
        m.scalar(xs, new int[]{1, 2, 3, 4}, "=", z).post();

        m.count(x, xs, y).post();
        IntVar c = m.count("c", 3, xs);
        m.allDifferent(xs, "BC").post();
        m.allDifferent(xs, "NEQS").post();
        m.allDifferentExceptValues(xs, 0, 9).post();
        m.allDiffPrec(xs, new boolean[][]{{false, true, false, false}, {false, false, false, false},
                {false, false, false, false}, {false, false, false, false}}).post();
        IntVar[] shifted = new IntVar[4];
        for (int i = 0; i < 4; i++) shifted[i] = m.offset(xs[i], i);
        m.allDifferent(shifted).post();

        IntVar el = m.element("el", new int[]{4, 5, 6}, x);
        m.element(y, grid[0], x, 0).post();
        m.element(z, grid, x, 0, y, 0);
        m.clausesIntChanneling(x, m.boolVarArray(10), m.boolVarArray(10)).post();
        m.setsIntsChanneling(ss, xs).post();

        m.keySort(new IntVar[][]{{x, y}, {z, w}}, null, new IntVar[][]{m.intVarArray(2, 0, 9), m.intVarArray(2, 0, 9)}, 1).post();
        m.lexChainLess(grid).post();
        m.intValuePrecedeChain(xs, 1, 2).post();
        IntVar mx = m.max("mx", xs), mn = m.min("mn", xs);
        IntVar am = m.argmax("am", xs), an = m.argmin("an", xs);

        m.ifThen(b, m.arithm(x, ">", 2));
        m.ifThenElse(b, m.arithm(x, ">", 2), m.arithm(x, "<", 1));
        m.and(bs).post();
        m.and(m.arithm(x, ">", 1), m.arithm(y, ">", 1)).post();
        m.or(bs).post();
        BoolVar r = m.arithm(x, ">", 1).reify();
        m.reifyXeqY(x, y, b);
        m.reifyXneC(x, 3, b);
        m.reifyXltYC(x, y, 2, b);
        m.reifXrelC(x, ">=", 3, b);
        m.reifXrelYC(x, "<", y, 1, b);
        m.impXrelC(x, ">=", 3, b);
        m.impXrelYC(x, "<", y, 1, b);
        m.addClauses(org.chocosolver.solver.constraints.nary.cnf.LogOp.or(bs[0], org.chocosolver.solver.constraints.nary.cnf.LogOp.and(bs[1], bs[2].not())));
        m.addClauses(new BoolVar[]{bs[0]}, new BoolVar[]{bs[1]});
        m.addClausesBoolOrArrayEqualTrue(bs);
        m.addClausesAtMostOne(bs);
        m.addClausesBoolAndArrayEqVar(bs, b);
        m.addConstructiveDisjunction(m.arithm(x, "<", 2), m.arithm(x, ">", 7));

        Tuples tuples = new Tuples(true);
        tuples.add(0, 1);
        m.table(x, y, tuples).post();
        m.table(new IntVar[]{x, y}, tuples, "MDD+").post();
        FiniteAutomaton fa = new FiniteAutomaton();
        int q0 = fa.addState(), q1 = fa.addState();
        fa.setInitialState(q0);
        fa.setFinal(q1);
        fa.addTransition(q0, q1, 1, 2);
        fa.addTransition(q1, q1, 0);
        m.regular(xs, fa).post();
        m.regular(xs, new FiniteAutomaton("(1|2){2,3}0?", 0, 9)).post();
        m.costRegular(xs, z, org.chocosolver.solver.constraints.nary.automata.FA.CostAutomaton.makeSingleResource(
                fa, new int[4][10][2], 0, 100)).post();

        m.circuit(xs, 0, org.chocosolver.solver.constraints.nary.circuit.CircuitConf.RD).post();
        m.path(xs, x, y, 1).post();
        m.subPath(xs, x, y, 0, z).post();
        m.tree(xs, x, 1).post();
        m.binPacking(xs, new int[]{1, 2, 3, 4}, ys, 1).post();
        m.cumulative(new Task[]{t, t2, opt}, new IntVar[]{m.intVar(1), m.intVar(2), m.intVar(1)}, m.intVar(2)).post();
        m.cumulative(java.util.List.of(t, t2), java.util.List.of(m.intVar(1), m.intVar(1)), m.intVar(1)).post();
        m.diffN(new IntVar[][]{{x, y}, {z, w}}, new int[][]{{1, 1}, {2, 2}}).post();

        m.cumulativeDec(xs, ys, xs, z);
        m.disjunctiveDec(new Task[]{t, t2}, true);
        m.ifThenElseDec(bs, new int[]{1, 2, 3, 4}, z);
        m.product(new IntVar[][]{{x}}, new IntVar[][]{{y}}, new IntVar[][]{{z}});
        m.globalCardinalityDec(xs, new IntVar[]{m.intVar(1), m.intVar(2)}, ys, false);

        m.union(ss, s).post();
        m.union(xs, s).post();
        m.intersection(ss, s).post();
        m.subsetEq(ss).post();
        m.disjoint(ss[0], ss[1]).post();
        m.allDisjoint(ss).post();
        m.partition(ss, s).post();
        m.notEmpty(s).post();
        m.nbEmpty(ss, x).post();
        m.member(x, s).post();
        m.member(2, s).post();
        m.notMember(x, s).post();
        m.sum(s, x).post();
        m.max(s, x, true).post();
        m.min(s, x, true).post();
        m.element(x, ss, s).post();
        m.offSet(ss[0], ss[1], 1).post();
        m.sortedSetIntsChanneling(s, xs, -1, 0).post();
        s.getCard().ge(1).post();

        Solver solver = m.getSolver();
        solver.setSearch(org.chocosolver.solver.search.strategy.Search.minDomLBSearch(xs),
                org.chocosolver.solver.search.strategy.Search.inputOrderUBSearch(ys));
        solver.setSearch(org.chocosolver.solver.search.strategy.Search.intVarSearch(
                new org.chocosolver.solver.search.strategy.selectors.variables.FirstFail(m),
                new org.chocosolver.solver.search.strategy.selectors.values.IntDomainMiddle(true), xs));
        solver.setSearch(org.chocosolver.solver.search.strategy.Search.intVarSearch(
                new org.chocosolver.solver.search.strategy.selectors.variables.Smallest(),
                new org.chocosolver.solver.search.strategy.selectors.values.IntDomainMax(), xs));
        solver.setSearch(org.chocosolver.solver.search.strategy.Search.intVarSearch(
                new org.chocosolver.solver.search.strategy.selectors.variables.MaxRegret(),
                new org.chocosolver.solver.search.strategy.selectors.values.IntDomainMedian(), xs));
        solver.setSearch(org.chocosolver.solver.search.strategy.Search.intVarSearch(
                new org.chocosolver.solver.search.strategy.selectors.variables.InputOrder<>(m),
                new org.chocosolver.solver.search.strategy.selectors.values.IntDomainRandom(1), xs));
        solver.setSearch(org.chocosolver.solver.search.strategy.Search.lastConflict(
                org.chocosolver.solver.search.strategy.Search.activityBasedSearch(xs)));
        solver.setSearch(org.chocosolver.solver.search.strategy.Search.conflictOrderingSearch(
                org.chocosolver.solver.search.strategy.Search.conflictHistorySearch(xs)));
        solver.setSearch(org.chocosolver.solver.search.strategy.Search.bestBound(
                org.chocosolver.solver.search.strategy.Search.failureRateBasedSearch(xs)));
        solver.setSearch(org.chocosolver.solver.search.strategy.Search.sequencer(
                org.chocosolver.solver.search.strategy.Search.domOverWDegRefSearch(xs),
                org.chocosolver.solver.search.strategy.Search.setVarSearch(s)));
        solver.setSearch(m.setTimes(new Task[]{t, t2}));
        solver.setSearch(org.chocosolver.solver.search.strategy.Search.roundRobinSearch(xs));
        solver.setGeometricalRestart(10, 1.2, new FailCounter(m, 1), 1000);
        solver.setLinearRestart(10, new FailCounter(m, 1), 1000);
        solver.setNoGoodRecordingFromRestarts();
        solver.limitTime("10s");
        solver.limitFail(1000);
        boolean done = solver.getSearchState() == org.chocosolver.solver.search.SearchState.TERMINATED;
        m.setObjective(Model.MAXIMIZE, total);
    }

    public static void main(String[] args) {
        int[] table = {5, 7, 9};

        // ---- element
        check("element(v0, int[], v1)", 2, -1, 9,
              (m, v) -> m.element(v[0], table, v[1]).post(),
              a -> a[1] >= 0 && a[1] < 3 && a[0] == table[a[1]]);
        check("element(v0, int[], v1, offset 1)", 2, -1, 9,
              (m, v) -> m.element(v[0], table, v[1], 1).post(),
              a -> a[1] >= 1 && a[1] <= 3 && a[0] == table[a[1] - 1]);
        check("element(v0, IntVar[] v2..v4, v1, 0)", 5, 0, 3,
              (m, v) -> m.element(v[0], slice(v, 2, 5), v[1], 0).post(),
              a -> a[1] < 3 && a[0] == a[2 + a[1]]);
        int[][] matrix = {{1, 2}, {3, 4}};
        // The 2D decomposition indexes the row-major flattening and does not
        // bound the column: (row 0, col 2) reads matrix[1][0]. Bound it.
        check("element 2D decomposition, column unbounded", 3, 0, 4,
              (m, v) -> m.element(v[0], matrix, v[1], 0, v[2], 0),
              a -> a[1] * 2 + a[2] < 4 && a[0] == matrix[(a[1] * 2 + a[2]) / 2][(a[1] * 2 + a[2]) % 2]);
        check("element 2D decomposition, column bounded", 3, 0, 4, (m, v) -> {
            m.arithm(v[2], "<", 2).post();
            m.element(v[0], matrix, v[1], 0, v[2], 0);
        }, a -> a[1] < 2 && a[2] < 2 && a[0] == matrix[a[1]][a[2]]);

        // ---- distinctness and equality
        check("allDifferent", 4, 0, 3, (m, v) -> m.allDifferent(v).post(), a -> distinct(a, 0, 4));
        check("allDifferent AC", 4, 0, 3, (m, v) -> m.allDifferent(v, "AC").post(), a -> distinct(a, 0, 4));
        check("allDifferentExcept0", 4, 0, 3, (m, v) -> m.allDifferentExcept0(v).post(), a -> {
            for (int i = 0; i < 4; i++) for (int j = i + 1; j < 4; j++) if (a[i] != 0 && a[i] == a[j]) return false;
            return true;
        });
        check("allEqual", 3, 0, 3, (m, v) -> m.allEqual(v).post(), a -> a[0] == a[1] && a[1] == a[2]);
        check("notAllEqual", 3, 0, 3, (m, v) -> m.notAllEqual(v).post(), a -> !(a[0] == a[1] && a[1] == a[2]));

        // ---- counting
        check("count(2, v1..v4, v0)", 5, 0, 3, (m, v) -> m.count(2, slice(v, 1, 5), v[0]).post(),
              a -> a[0] == occurrences(a, 1, 5, 2));
        check("count(v1, v2..v4, v0)", 5, 0, 3, (m, v) -> m.count(v[1], slice(v, 2, 5), v[0]).post(),
              a -> a[0] == occurrences(a, 2, 5, a[1]));
        check("among(v0, v1..v4, {1,3})", 5, 0, 3, (m, v) -> m.among(v[0], slice(v, 1, 5), new int[]{1, 3}).post(),
              a -> a[0] == occurrences(a, 1, 5, 1) + occurrences(a, 1, 5, 3));
        check("globalCardinality open", 5, 0, 3,
              (m, v) -> m.globalCardinality(slice(v, 0, 3), new int[]{1, 2}, slice(v, 3, 5), false).post(),
              a -> a[3] == occurrences(a, 0, 3, 1) && a[4] == occurrences(a, 0, 3, 2));
        check("globalCardinality closed", 5, 0, 3,
              (m, v) -> m.globalCardinality(slice(v, 0, 3), new int[]{1, 2}, slice(v, 3, 5), true).post(),
              a -> a[3] == occurrences(a, 0, 3, 1) && a[4] == occurrences(a, 0, 3, 2)
                      && a[3] + a[4] == 3);
        check("nValues(v1..v4, v0)", 5, 0, 3, (m, v) -> m.nValues(slice(v, 1, 5), v[0]).post(),
              a -> a[0] == nvalues(a, 1, 5));
        check("atMostNValues(v1..v4, v0)", 5, 0, 3, (m, v) -> m.atMostNValues(slice(v, 1, 5), v[0], false).post(),
              a -> nvalues(a, 1, 5) <= a[0]);
        check("atLeastNValues(v1..v4, v0)", 5, 0, 3, (m, v) -> m.atLeastNValues(slice(v, 1, 5), v[0], false).post(),
              a -> nvalues(a, 1, 5) >= a[0]);

        // ---- min, max, arg
        check("max(v0, v1..v3)", 4, 0, 3, (m, v) -> m.max(v[0], slice(v, 1, 4)).post(),
              a -> a[0] == Math.max(a[1], Math.max(a[2], a[3])));
        check("min(v0, v1..v3)", 4, 0, 3, (m, v) -> m.min(v[0], slice(v, 1, 4)).post(),
              a -> a[0] == Math.min(a[1], Math.min(a[2], a[3])));
        check("argmax(v0, 0, v1..v3): first index", 4, 0, 3, (m, v) -> m.argmax(v[0], 0, slice(v, 1, 4)).post(), a -> {
            int best = 0;
            for (int i = 1; i < 3; i++) if (a[1 + i] > a[1 + best]) best = i;
            return a[0] == best;
        });
        check("argmin(v0, 1, v1..v3): first index + 1", 4, 0, 3, (m, v) -> m.argmin(v[0], 1, slice(v, 1, 4)).post(), a -> {
            int best = 0;
            for (int i = 1; i < 3; i++) if (a[1 + i] < a[1 + best]) best = i;
            return a[0] == best + 1;
        });

        // ---- arithmetic
        check("arithm(v0, +, v1, =, v2)", 3, -2, 3, (m, v) -> m.arithm(v[0], "+", v[1], "=", v[2]).post(),
              a -> a[0] + a[1] == a[2]);
        check("arithm(v0, -, v1, <=, 1)", 2, -2, 3, (m, v) -> m.arithm(v[0], "-", v[1], "<=", 1).post(),
              a -> a[0] - a[1] <= 1);
        check("times(v0, v1, v2)", 3, -3, 4, (m, v) -> m.times(v[0], v[1], v[2]).post(), a -> a[0] * a[1] == a[2]);
        check("div(v0, v1, v2): truncates toward 0", 3, -4, 4, (m, v) -> m.div(v[0], v[1], v[2]).post(),
              a -> a[1] != 0 && a[0] / a[1] == a[2]);
        check("mod(v0, v1, v2): sign of dividend", 3, -4, 4, (m, v) -> m.mod(v[0], v[1], v[2]).post(),
              a -> a[1] != 0 && a[0] % a[1] == a[2]);
        check("mod(v0, 3, v1)", 2, -4, 4, (m, v) -> m.mod(v[0], 3, v[1]).post(), a -> a[0] % 3 == a[1]);
        check("absolute(v0, v1)", 2, -3, 3, (m, v) -> m.absolute(v[0], v[1]).post(), a -> a[0] == Math.abs(a[1]));
        check("square(v0, v1)", 2, -3, 9, (m, v) -> m.square(v[0], v[1]).post(), a -> a[0] == a[1] * a[1]);
        check("pow(v0, 2, v1)", 2, -3, 9, (m, v) -> m.pow(v[0], 2, v[1]).post(), a -> a[1] == a[0] * a[0]);
        check("distance(v0, v1, =, 2)", 2, -3, 3, (m, v) -> m.distance(v[0], v[1], "=", 2).post(),
              a -> Math.abs(a[0] - a[1]) == 2);
        check("sum(v0..v2, =, v3)", 4, -1, 3, (m, v) -> m.sum(slice(v, 0, 3), "=", v[3]).post(),
              a -> a[0] + a[1] + a[2] == a[3]);
        check("scalar(v0..v2, {2,-1,3}, <=, 4)", 3, -1, 3,
              (m, v) -> m.scalar(slice(v, 0, 3), new int[]{2, -1, 3}, "<=", 4).post(),
              a -> 2 * a[0] - a[1] + 3 * a[2] <= 4);
        check("sum(BoolVar[], >=, 2)", 4, 0, 1, (m, v) -> m.sum(bools(m, v), ">=", 2).post(),
              a -> a[0] + a[1] + a[2] + a[3] >= 2);
        check("member(v0, {1,3})", 1, 0, 4, (m, v) -> m.member(v[0], new int[]{1, 3}).post(), a -> a[0] == 1 || a[0] == 3);
        check("notMember(v0, 1, 3)", 1, 0, 4, (m, v) -> m.notMember(v[0], 1, 3).post(), a -> a[0] < 1 || a[0] > 3);

        // ---- expressions
        check("v0.mul(v1).add(v2).eq(4)", 3, -2, 3, (m, v) -> v[0].mul(v[1]).add(v[2]).eq(4).post(),
              a -> a[0] * a[1] + a[2] == 4);
        check("v0.dist(v1).le(1).or(v2.eq(0))", 3, 0, 3, (m, v) -> v[0].dist(v[1]).le(1).or(v[2].eq(0)).post(),
              a -> Math.abs(a[0] - a[1]) <= 1 || a[2] == 0);
        check("v0.gt(v1).imp(v2.eq(3))", 3, 0, 3, (m, v) -> v[0].gt(v[1]).imp(v[2].eq(3)).post(),
              a -> !(a[0] > a[1]) || a[2] == 3);
        check("v0.max(v1).sub(v2).abs().eq(1)", 3, 0, 3, (m, v) -> v[0].max(v[1]).sub(v[2]).abs().eq(1).post(),
              a -> Math.abs(Math.max(a[0], a[1]) - a[2]) == 1);
        check("v0.eq(v1.ift(v2, 3)) [ift on Bool]", 3, 0, 3,
              (m, v) -> v[0].eq(v[1].eq(1).ift(v[2], 3)).post(),
              a -> a[0] == (a[1] == 1 ? a[2] : 3));
        check("v0.eq(v1.div(2))", 2, -3, 3, (m, v) -> v[0].eq(v[1].div(2)).post(), a -> a[0] == a[1] / 2);

        // ---- reification and logic
        check("ifThen(v0 > 1, v1 = 0)", 2, 0, 3, (m, v) -> m.ifThen(m.arithm(v[0], ">", 1), m.arithm(v[1], "=", 0)),
              a -> a[0] <= 1 || a[1] == 0);
        check("ifThenElse(v0 = 0, v1 = 1, v1 = 2)", 2, 0, 3,
              (m, v) -> m.ifThenElse(m.arithm(v[0], "=", 0), m.arithm(v[1], "=", 1), m.arithm(v[1], "=", 2)),
              a -> a[0] == 0 ? a[1] == 1 : a[1] == 2);
        check("ifOnlyIf(v0 = 0, v1 = 0)", 2, 0, 3, (m, v) -> m.ifOnlyIf(m.arithm(v[0], "=", 0), m.arithm(v[1], "=", 0)),
              a -> (a[0] == 0) == (a[1] == 0));
        check("reifyWith: v2 = [v0 < v1]", 3, 0, 2, (m, v) -> {
            BoolVar b = m.boolVar();
            m.arithm(v[0], "<", v[1]).reifyWith(b);
            m.arithm(b, "=", v[2]).post();
        }, a -> a[2] == (a[0] < a[1] ? 1 : 0));
        check("c.implies(b): [v0 = v1] -> v2 = 1", 3, 0, 2, (m, v) -> {
            BoolVar b = m.boolVar();
            m.arithm(b, "=", v[2]).post();
            m.arithm(v[0], "=", v[1]).implies(b);
        }, a -> a[2] <= 1 && (a[0] != a[1] || a[2] == 1));
        check("c.impliedBy(b): v2 = 1 -> [v0 = v1]", 3, 0, 2, (m, v) -> {
            BoolVar b = m.boolVar();
            m.arithm(b, "=", v[2]).post();
            m.arithm(v[0], "=", v[1]).impliedBy(b);
        }, a -> a[2] <= 1 && (a[2] == 0 || a[0] == a[1]));
        check("or(constraints)", 2, 0, 3, (m, v) -> m.or(m.arithm(v[0], "=", 1), m.arithm(v[1], "=", 2)).post(),
              a -> a[0] == 1 || a[1] == 2);
        check("not(allDifferent)", 3, 0, 2, (m, v) -> m.not(m.allDifferent(v)).post(), a -> !distinct(a, 0, 3));

        // ---- channelling
        check("inverseChanneling(v0..v2, v3..v5)", 6, 0, 2,
              (m, v) -> m.inverseChanneling(slice(v, 0, 3), slice(v, 3, 6)).post(), a -> {
                  for (int i = 0; i < 3; i++) if (a[3 + a[i]] != i) return false;
                  return true;
              });
        check("inverseChanneling offsets (1, 0): v[i] = j+1 <=> w[j] = i", 6, 0, 3,
              (m, v) -> m.inverseChanneling(slice(v, 0, 3), slice(v, 3, 6), 1, 0).post(), a -> {
                  for (int i = 0; i < 3; i++) {
                      int j = a[i] - 1;
                      if (j < 0 || j >= 3 || a[3 + j] != i) return false;
                  }
                  return true;
              });
        check("boolsIntChanneling(v1..v3, v0, offset 1)", 4, 0, 3,
              (m, v) -> m.boolsIntChanneling(bools(m, slice(v, 1, 4)), v[0], 1).post(), a -> {
                  // Also forces v0 into [offset, offset + n): exactly one Boolean is 1.
                  for (int i = 0; i < 3; i++) if ((a[1 + i] == 1) != (a[0] == i + 1)) return false;
                  return a[1] <= 1 && a[2] <= 1 && a[3] <= 1 && a[0] >= 1;
              });
        check("bitsIntChanneling(v1..v3, v0): v0 = sum 2^i", 4, 0, 7,
              (m, v) -> m.bitsIntChanneling(bools(m, slice(v, 1, 4)), v[0]).post(),
              a -> a[1] <= 1 && a[2] <= 1 && a[3] <= 1 && a[0] == a[1] + 2 * a[2] + 4 * a[3]);

        // ---- ordering
        check("increasing(v, 0): nondecreasing", 3, 0, 3, (m, v) -> m.increasing(v, 0).post(),
              a -> a[0] <= a[1] && a[1] <= a[2]);
        check("increasing(v, 1): strictly", 3, 0, 3, (m, v) -> m.increasing(v, 1).post(),
              a -> a[0] < a[1] && a[1] < a[2]);
        check("decreasing(v, 0)", 3, 0, 3, (m, v) -> m.decreasing(v, 0).post(), a -> a[0] >= a[1] && a[1] >= a[2]);
        check("sort(v0..v2, v3..v5)", 6, 0, 2, (m, v) -> m.sort(slice(v, 0, 3), slice(v, 3, 6)).post(), a -> {
            int[] s = Arrays.copyOfRange(a, 0, 3);
            Arrays.sort(s);
            return a[3] == s[0] && a[4] == s[1] && a[5] == s[2];
        });
        check("lexLess(v0..v1, v2..v3)", 4, 0, 2, (m, v) -> m.lexLess(slice(v, 0, 2), slice(v, 2, 4)).post(),
              a -> a[0] < a[2] || (a[0] == a[2] && a[1] < a[3]));
        check("lexLessEq", 4, 0, 2, (m, v) -> m.lexLessEq(slice(v, 0, 2), slice(v, 2, 4)).post(),
              a -> a[0] < a[2] || (a[0] == a[2] && a[1] <= a[3]));
        check("lexChainLessEq(3 rows of 2)", 6, 0, 1,
              (m, v) -> m.lexChainLessEq(slice(v, 0, 2), slice(v, 2, 4), slice(v, 4, 6)).post(),
              a -> (a[0] < a[2] || (a[0] == a[2] && a[1] <= a[3])) && (a[2] < a[4] || (a[2] == a[4] && a[3] <= a[5])));
        check("intValuePrecedeChain(v, {1, 2})", 4, 0, 2,
              (m, v) -> m.intValuePrecedeChain(v, new int[]{1, 2}).post(), a -> {
                  int first1 = 5, first2 = 5;
                  for (int i = 3; i >= 0; i--) {
                      if (a[i] == 1) first1 = i;
                      if (a[i] == 2) first2 = i;
                  }
                  return first2 == 5 || first1 < first2;
              });

        // ---- graphs over successor variables
        check("circuit(v)", 4, 0, 3, (m, v) -> m.circuit(v).post(), a -> circuit(a, 0, 4, 0));
        check("circuit(v, offset 1)", 4, 1, 4, (m, v) -> m.circuit(v, 1).post(), a -> circuit(a, 0, 4, 1));
        check("subCircuit(v1..v4, 0, v0)", 5, 0, 3, (m, v) -> m.subCircuit(slice(v, 1, 5), 0, v[0]).post(), a -> {
            int n = 4, inCycle = 0, start = -1;
            for (int i = 0; i < n; i++) if (a[1 + i] != i) { inCycle++; start = i; }
            if (inCycle == 1) return false;
            if (a[0] != inCycle) return false;
            if (inCycle == 0) return true;
            int node = start;
            for (int step = 0; step < inCycle; step++) node = a[1 + node];
            if (node != start) return false;
            boolean[] seen = new boolean[n];
            node = start;
            for (int step = 0; step < inCycle; step++) {
                if (seen[node] || a[1 + node] == node) return false;
                seen[node] = true;
                node = a[1 + node];
            }
            return true;
        });
        check("path(v2..v5, v0, v1): succ[end] = n", 6, 0, 4, (m, v) -> m.path(slice(v, 2, 6), v[0], v[1]).post(), a -> {
            int n = 4, node = a[0];
            if (node >= n || a[1] >= n) return false;
            boolean[] seen = new boolean[n];
            for (int step = 0; step < n; step++) {
                if (seen[node]) return false;
                seen[node] = true;
                int next = a[2 + node];
                if (step == n - 1) return node == a[1] && next == n;
                if (next >= n) return false;
                node = next;
            }
            return false;
        });
        check("tree(v1..v3, v0): roots have succ[i] = i", 4, 0, 2, (m, v) -> m.tree(slice(v, 1, 4), v[0]).post(), a -> {
            int roots = 0;
            for (int i = 0; i < 3; i++) {
                if (a[1 + i] == i) roots++;
                int node = i;
                for (int step = 0; step < 3 && a[1 + node] != node; step++) node = a[1 + node];
                if (a[1 + node] != node) return false;
            }
            return a[0] == roots;
        });

        // ---- extensional
        Tuples allowed = new Tuples(true);
        allowed.add(new int[][]{{0, 1}, {1, 2}, {2, 0}});
        check("table(v, allowed)", 2, 0, 2, (m, v) -> m.table(v, allowed).post(),
              a -> (a[0] == 0 && a[1] == 1) || (a[0] == 1 && a[1] == 2) || (a[0] == 2 && a[1] == 0));
        Tuples forbidden = new Tuples(false);
        forbidden.add(new int[][]{{0, 1}, {1, 2}});
        check("table(v, forbidden)", 2, 0, 2, (m, v) -> m.table(v, forbidden).post(),
              a -> !((a[0] == 0 && a[1] == 1) || (a[0] == 1 && a[1] == 2)));
        // The universal value has to be given to the constructor: set later
        // with setUniversalValue it is read as an ordinary value.
        Tuples star = new Tuples(new int[][]{{0, -1}, {2, 1}}, true, java.util.OptionalInt.of(-1));
        check("table with universal value -1", 2, 0, 2, (m, v) -> m.table(v, star).post(),
              a -> a[0] == 0 || (a[0] == 2 && a[1] == 1));
        check("regular(v, \"0*1+0*\")", 4, 0, 1, (m, v) -> m.regular(v, new FiniteAutomaton("0*1+0*")).post(), a -> {
            String s = "" + a[0] + a[1] + a[2] + a[3];
            return s.matches("0*1+0*");
        });
        check("regular(v, \"<10>2*\") multi-digit symbol", 3, 2, 10,
              (m, v) -> m.regular(v, new FiniteAutomaton("<10>2*")).post(),
              a -> a[0] == 10 && a[1] == 2 && a[2] == 2);

        // ---- packing and scheduling
        int[] sizes = {2, 1, 2};
        check("binPacking(v0..v2, {2,1,2}, v3..v4, 0)", 5, 0, 3,
              (m, v) -> m.binPacking(slice(v, 0, 3), sizes, slice(v, 3, 5), 0).post(), a -> {
                  int[] load = new int[2];
                  for (int i = 0; i < 3; i++) {
                      if (a[i] > 1) return false;
                      load[a[i]] += sizes[i];
                  }
                  return a[3] == load[0] && a[4] == load[1];
              });
        int[] dur = {2, 1, 2}, height = {1, 2, 1};
        check("cumulative(starts, {2,1,2}, {1,2,1}, cap 2)", 3, 0, 3,
              (m, v) -> m.cumulative(v, dur, height, 2).post(), a -> {
                  for (int t = 0; t < 6; t++) {
                      int used = 0;
                      for (int i = 0; i < 3; i++) if (a[i] <= t && t < a[i] + dur[i]) used += height[i];
                      if (used > 2) return false;
                  }
                  return true;
              });
        check("cumulative(Task[], heights, capacity) with capacity 1", 3, 0, 4, (m, v) -> {
            Task[] tasks = new Task[3];
            IntVar[] h = new IntVar[3];
            for (int i = 0; i < 3; i++) {
                tasks[i] = new Task(v[i], dur[i]);
                h[i] = m.intVar(1);
            }
            m.cumulative(tasks, h, m.intVar(1)).post();
        }, a -> {
            for (int i = 0; i < 3; i++)
                for (int j = i + 1; j < 3; j++)
                    if (a[i] < a[j] + dur[j] && a[j] < a[i] + dur[i]) return false;
            return true;
        });
        check("diffN(x, y, w, h, true): 2x1 and 1x2 boxes", 4, 0, 2, (m, v) -> {
            IntVar[] w = {m.intVar(2), m.intVar(1)};
            IntVar[] h = {m.intVar(1), m.intVar(2)};
            m.diffN(new IntVar[]{v[0], v[1]}, new IntVar[]{v[2], v[3]}, w, h, true).post();
        }, a -> {
            int x0 = a[0], x1 = a[1], y0 = a[2], y1 = a[3];
            return x0 + 2 <= x1 || x1 + 1 <= x0 || y0 + 1 <= y1 || y1 + 2 <= y0;
        });
        check("knapsack(v1..v2, weightSum v0, energySum v3, w {2,3}, e {1,4})", 4, 0, 8,
              (m, v) -> m.knapsack(slice(v, 1, 3), v[0], v[3], new int[]{2, 3}, new int[]{1, 4}).post(),
              a -> a[0] == 2 * a[1] + 3 * a[2] && a[3] == a[1] + 4 * a[2]);

        // ---- sets, channelled to Booleans
        check("setBoolsChanneling + cardinality 2", 3, 0, 1, (m, v) -> {
            SetVar s = m.setVar(new int[]{}, new int[]{0, 1, 2});
            m.setBoolsChanneling(bools(m, v), s).post();
            s.getCard().eq(2).post();
        }, a -> a[0] + a[1] + a[2] == 2);
        check("sumElements(set, weights, v0)", 4, 0, 6, (m, v) -> {
            SetVar s = m.setVar(new int[]{}, new int[]{0, 1, 2});
            m.setBoolsChanneling(bools(m, slice(v, 1, 4)), s).post();
            m.sumElements(s, new int[]{1, 2, 3}, v[0]).post();
        }, a -> a[1] <= 1 && a[2] <= 1 && a[3] <= 1 && a[0] == a[1] + 2 * a[2] + 3 * a[3]);

        System.out.println();
        System.out.println(failures == 0 ? "all checks agree with brute force" : failures + " checks FAILED");
        System.out.println("not usable under LCG: " + lcgUnsupported);
        if (failures > 0) System.exit(1);
    }
}
