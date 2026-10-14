import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;

public class Probe3 {
    public static void main(String[] a) {
        Store st = new Store();
        IntVar big = new IntVar(st, "big", 0, 1_000_000_000);
        System.out.println("big: " + big + " consistency=" + st.consistency());
        // zero weights and repeated vars in LinearInt
        st = new Store();
        IntVar x = new IntVar(st, "x", 0, 5), y = new IntVar(st, "y", 0, 5);
        st.impose(new LinearInt(new IntVar[]{x, y, x}, new int[]{1, 0, 1}, "==", 6));
        DepthFirstSearch<IntVar> s = new DepthFirstSearch<>(); s.setPrintInfo(false);
        System.out.println("zero weight: " + s.labeling(st, new SimpleSelect<>(new IntVar[]{x, y}, null, new IndomainMin<>())) + " " + x + " " + y);
        // empty LinearInt
        try {
            st = new Store();
            st.impose(new LinearInt(new IntVar[]{}, new int[]{}, "<=", 0));
            System.out.println("empty linear consistency=" + st.consistency());
        } catch (Exception e) { System.out.println("empty linear: " + e); }
        // deep search
        int n = Integer.parseInt(a[0]);
        st = new Store();
        IntVar[] v = new IntVar[n];
        for (int i = 0; i < n; i++) v[i] = new IntVar(st, 0, 1);
        for (int i = 0; i + 1 < n; i++) st.impose(new XneqY(v[i], v[i + 1]));
        s = new DepthFirstSearch<>(); s.setPrintInfo(false);
        try {
            System.out.println("deep " + n + ": " + s.labeling(st, new SimpleSelect<>(v, null, new IndomainMin<>())));
        } catch (StackOverflowError e) { System.out.println("deep " + n + ": StackOverflowError"); }
        // logical constraints
        st = new Store();
        x = new IntVar(st, "x", 0, 5); y = new IntVar(st, "y", 0, 5);
        st.impose(new Or(new XeqC(x, 1), new XeqC(y, 1)));
        st.impose(new IfThen(new XgtC(x, 0), new XltY(x, y)));
        st.impose(new Not(new XeqY(x, y)));
        BooleanVar b = new BooleanVar(st);
        st.impose(new Implies(b, new XgteqC(y, 3)));
        st.impose(new XeqC(b, 1));
        st.impose(new org.jacop.constraints.table.Table(new IntVar[]{x, y}, new int[][]{{0, 1}, {1, 3}, {1, 4}}));
        s = new DepthFirstSearch<>(); s.setPrintInfo(false);
        System.out.println("logic: " + s.labeling(st, new SimpleSelect<>(new IntVar[]{x, y}, null, new IndomainMin<>())) + " " + x + " " + y);
    }
}
