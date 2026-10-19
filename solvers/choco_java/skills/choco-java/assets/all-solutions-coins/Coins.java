// Count the ways to pay 10 with any number of coins worth 1, 2 and 5, where only the
// number of coins of each kind matters. Shows: enumeration with solve() in a loop,
// bounded integer variables, scalar as the payment rule, and why the counts are the
// only decision variables (the amount is fixed by them, so nothing repeats).
import org.chocosolver.solver.Model;
import org.chocosolver.solver.Solver;
import org.chocosolver.solver.variables.IntVar;

public class Coins {
    public static void main(String[] args) {
        int[] value = {1, 2, 5};
        int amount = 10;
        Model m = new Model("coins");
        IntVar[] count = m.intVarArray("count", value.length, 0, amount);

        // the coins pay exactly the amount
        m.scalar(count, value, "=", m.intVar(amount)).post();

        Solver s = m.getSolver();
        int ways = 0;
        while (s.solve()) {
            ways++;
            StringBuilder line = new StringBuilder("  ");
            for (int k = 0; k < value.length; k++)
                line.append(value[k]).append("s=").append(count[k].getValue()).append(' ');
            System.out.println(line.toString().trim());
        }
        System.out.println("Ways to pay " + amount + " with coins " + java.util.Arrays.toString(value) + ": " + ways);
    }
}
