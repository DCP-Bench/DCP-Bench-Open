import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;

public class Probe {
    static void p(Object o) { System.out.println(o); }

    public static void main(String[] a) {
        // 1. satisfy
        Store store = new Store();
        IntVar x = new IntVar(store, "x", 0, 2), y = new IntVar(store, "y", 0, 2);
        store.impose(new XplusYeqC(x, y, 2));
        DepthFirstSearch<IntVar> s = new DepthFirstSearch<>();
        s.setPrintInfo(false);
        boolean ok = s.labeling(store, new SimpleSelect<>(new IntVar[]{x, y}, null, new IndomainMin<>()));
        p("satisfy " + ok + " x=" + x.value() + " y=" + y.value() + " level=" + store.level);

        // 2. enumerate all
        store = new Store();
        x = new IntVar(store, "x", 0, 2); y = new IntVar(store, "y", 0, 2);
        store.impose(new XplusYeqC(x, y, 2));
        s = new DepthFirstSearch<>(); s.setPrintInfo(false);
        s.getSolutionListener().searchAll(true);
        s.getSolutionListener().recordSolutions(true);
        ok = s.labeling(store, new SimpleSelect<>(new IntVar[]{x, y}, null, new IndomainMin<>()));
        p("all " + ok + " count=" + s.getSolutionListener().solutionsNo());

        // 3. minimise and maximise
        for (int dir : new int[]{1, -1}) {
            store = new Store();
            x = new IntVar(store, "x", 0, 2); y = new IntVar(store, "y", 0, 2);
            IntVar t = new IntVar(store, "t", -4, 4);
            store.impose(new XplusYgtC(x, y, 0));
            store.impose(new LinearInt(new IntVar[]{x, y, t}, new int[]{dir, dir, -1}, "==", 0));
            s = new DepthFirstSearch<>(); s.setPrintInfo(false);
            ok = s.labeling(store, new SimpleSelect<>(new IntVar[]{x, y}, null, new IndomainMin<>()), t);
            p("opt dir=" + dir + " ok=" + ok + " cost=" + s.getCostValue() + " x=" + x.value() + " y=" + y.value() + " t=" + t + " timeout=" + s.timeOutOccured);
        }

        // 4. infeasible
        store = new Store();
        x = new IntVar(store, "x", 0, 1);
        store.impose(new XeqC(x, 0)); store.impose(new XeqC(x, 1));
        p("consistency " + store.consistency());
        s = new DepthFirstSearch<>(); s.setPrintInfo(false);
        ok = s.labeling(store, new SimpleSelect<>(new IntVar[]{x}, null, new IndomainMin<>()));
        p("infeasible " + ok);

        // 5. resolve with blocking at base level
        store = new Store();
        x = new IntVar(store, "x", 0, 2); y = new IntVar(store, "y", 0, 2);
        store.impose(new XplusYeqC(x, y, 2));
        int base = store.level;
        for (int i = 0; i < 5; i++) {
            store.setLevel(base + 1);
            s = new DepthFirstSearch<>(); s.setPrintInfo(false);
            ok = s.labeling(store, new SimpleSelect<>(new IntVar[]{x, y}, null, new IndomainMin<>()));
            int vx = ok ? x.value() : -1, vy = ok ? y.value() : -1;
            p("resolve " + i + " ok=" + ok + " x=" + vx + " y=" + vy + " level=" + store.level);
            store.removeLevel(base + 1); store.setLevel(base);
            p("  after restore x=" + x + " y=" + y);
            if (!ok) break;
            store.impose(new Or(new PrimitiveConstraint[]{new XneqC(x, vx), new XneqC(y, vy)}));
        }

        // 6. timeout on pigeonhole
        store = new Store();
        IntVar[] b = new IntVar[40];
        for (int i = 0; i < 40; i++) b[i] = new IntVar(store, 0, 38);
        for (int i = 0; i < 40; i++) for (int j = i + 1; j < 40; j++) store.impose(new XneqY(b[i], b[j]));
        s = new DepthFirstSearch<>(); s.setPrintInfo(false);
        s.setTimeOutMilliseconds(1500);
        long t0 = System.nanoTime();
        ok = s.labeling(store, new SimpleSelect<>(b, null, new IndomainMin<>()));
        p("pigeon ok=" + ok + " timeout=" + s.timeOutOccured + " secs=" + (System.nanoTime() - t0) / 1e9);
        p("store vars size=" + store.size() + " vars.length=" + store.vars.length);
    }
}
