import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;
import java.util.*;

public class Probe2 {
    public static void main(String[] a) {
        // Element default indexing
        Store st = new Store();
        IntVar i = new IntVar(st, "i", -5, 5), v = new IntVar(st, "v", 0, 100);
        st.impose(new Element(i, new int[]{10, 20, 30}, v));
        st.impose(new XeqC(v, 10));
        st.consistency();
        System.out.println("element default: " + i);
        st = new Store();
        i = new IntVar(st, "i", -5, 5); v = new IntVar(st, "v", 0, 100);
        st.impose(new ElementInteger(i, new int[]{10, 20, 30}, v, -1));
        st.impose(new XeqC(v, 10)); st.consistency();
        System.out.println("element offset -1: " + i);

        // Circuit domain
        st = new Store();
        IntVar[] nx = new IntVar[3];
        for (int k = 0; k < 3; k++) nx[k] = new IntVar(st, "n" + k, 0, 3);
        st.impose(new Circuit(nx)); st.consistency();
        System.out.println("circuit: " + Arrays.toString(nx));

        // default printing of labeling
        st = new Store();
        IntVar x = new IntVar(st, "x", 0, 2), y = new IntVar(st, "y", 0, 2);
        st.impose(new XplusYeqC(x, y, 2));
        System.out.println("--- default print begin");
        new DepthFirstSearch<IntVar>().labeling(st, new SimpleSelect<>(new IntVar[]{x, y}, null, new IndomainMin<>()));
        System.out.println("--- default print end");

        // all solutions via listener with dedupe on outputs, aux var t
        st = new Store();
        x = new IntVar(st, "x", 0, 2); y = new IntVar(st, "y", 0, 2);
        IntVar t = new IntVar(st, "t", 0, 1);
        st.impose(new XplusYeqC(x, y, 2));
        final IntVar fx = x, fy = y;
        Set<List<Integer>> seen = new LinkedHashSet<>();
        DepthFirstSearch<IntVar> s = new DepthFirstSearch<>();
        s.setPrintInfo(false);
        s.setSolutionListener(new SimpleSolutionListener<IntVar>() {
            @Override public boolean executeAfterSolution(Search<IntVar> search, SelectChoicePoint<IntVar> select) {
                boolean r = super.executeAfterSolution(search, select);
                seen.add(List.of(fx.value(), fy.value()));
                return r;
            }
        });
        s.getSolutionListener().searchAll(true);
        s.getSolutionListener().recordSolutions(false);
        boolean ok = s.labeling(st, new SimpleSelect<>(new IntVar[]{x, y, t}, null, new IndomainMin<>()));
        System.out.println("all: ok=" + ok + " solutionsNo=" + s.getSolutionListener().solutionsNo() + " distinct=" + seen);
        System.out.println("after searchAll x=" + x + " level=" + st.level);

        // maximise via negation with XmulCeqZ
        st = new Store();
        x = new IntVar(st, "x", 0, 5); y = new IntVar(st, "y", 0, 5);
        st.impose(new XplusYlteqZ(x, y, new IntVar(st, 7, 7)));
        IntVar obj = new IntVar(st, "obj", 0, 30);
        st.impose(new LinearInt(new IntVar[]{x, y, obj}, new int[]{3, 2, -1}, "==", 0));
        IntVar neg = new IntVar(st, "neg", -30, 0);
        st.impose(new XmulCeqZ(obj, -1, neg));
        s = new DepthFirstSearch<>(); s.setPrintInfo(false);
        ok = s.labeling(st, new SimpleSelect<>(new IntVar[]{x, y}, null, new IndomainMin<>()), neg);
        System.out.println("max ok=" + ok + " obj=" + obj + " x=" + x + " y=" + y + " cost=" + s.getCostValue() + " to=" + s.timeOutOccured);

        // Reified with BooleanVar, Implies, Count, SumInt
        st = new Store();
        IntVar[] q = new IntVar[4];
        for (int k = 0; k < 4; k++) q[k] = new IntVar(st, "q" + k, 0, 3);
        BooleanVar b = new BooleanVar(st, "b");
        st.impose(new Reified(new XeqC(q[0], 2), b));
        st.impose(new XeqC(b, 1));
        IntVar cnt = new IntVar(st, "cnt", 0, 4);
        st.impose(new Count(q, cnt, 2));
        IntVar sum = new IntVar(st, "sum", 0, 12);
        st.impose(new SumInt(q, "==", sum));
        st.impose(new XeqC(sum, 12 - 1));
        s = new DepthFirstSearch<>(); s.setPrintInfo(false);
        ok = s.labeling(st, new SimpleSelect<>(q, null, new IndomainMin<>()));
        System.out.println("reif ok=" + ok + " " + Arrays.toString(q) + " b=" + b + " cnt=" + cnt + " sum=" + sum);

        // value out of range
        try {
            st = new Store();
            new IntVar(st, "big", 0, 1_000_000_000);
            System.out.println("big var created");
        } catch (Exception e) { System.out.println("big var: " + e); }
    }
}
