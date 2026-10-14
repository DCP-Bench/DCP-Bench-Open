import org.jacop.core.*;
import org.jacop.constraints.*;
public class Probe4 {
    public static void main(String[] a) {
        Store st = new Store();
        IntVar x = new IntVar(st, "x", 0, 3);
        try { System.out.println("value of unfixed: " + x.value()); } catch (Throwable e) { System.out.println("value(): " + e); }
        IntVar[][] r = {{x, x, x, x}};
        st.impose(new Diff2(r)); st.impose(new Min(new IntVar[]{x}, x)); st.impose(new And(new XeqC(x, 1), new XltC(x, 3)));
        System.out.println("ok " + st.consistency() + " " + x);
    }
}
