import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;

public class Relevel {
    public static void main(String[] a) {
        for (int variant = 0; variant < 3; variant++) {
            Store store = new Store();
            IntVar x = new IntVar(store, "x", 0, 2), y = new IntVar(store, "y", 0, 2);
            store.impose(new XplusYgtC(x, y, 1));
            IntVar t = new IntVar(store, "t", 0, 4);
            store.impose(new XplusYeqZ(x, y, t));
            IntVar[] vars = {x, y, t};
            int base = store.level;
            store.setLevel(base + 1);
            DepthFirstSearch<IntVar> s = new DepthFirstSearch<>(); s.setPrintInfo(false);
            boolean ok = s.labeling(store, new SimpleSelect<>(vars, new SmallestDomain<>(), new IndomainMin<>()), t);
            System.out.println("variant " + variant + " opt " + ok + " " + x + " " + y + " " + t + " level " + store.level);
            store.removeLevel(base + 1); store.setLevel(base);
            System.out.println("  restored " + x + " " + y + " " + t);
            if (variant == 1) { store.setLevel(base + 1); }
            store.impose(new XeqC(t, 2));
            if (variant == 2) { System.out.println("  consistency " + store.consistency() + " " + t); }
            for (int i = 0; i < 4; i++) {
                store.setLevel(store.level + 1);
                int lv = store.level;
                s = new DepthFirstSearch<>(); s.setPrintInfo(false);
                ok = s.labeling(store, new SimpleSelect<>(vars, new SmallestDomain<>(), new IndomainMin<>()));
                System.out.println("  sol " + ok + " " + x + " " + y + " " + t);
                if (!ok) break;
                int vx = x.value(), vy = y.value();
                store.removeLevel(lv); store.setLevel(lv - 1);
                store.impose(new Or(new PrimitiveConstraint[]{new XneqC(x, vx), new XneqC(y, vy)}));
            }
        }
    }
}
