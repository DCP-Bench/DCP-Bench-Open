// Climbing stairs: climb a stair of n steps, taking between m1 and m2 steps per move, and list the steps of
// each move in order, with 0 for every move after the top is reached.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("n");       // number of steps of the stair
    int m1 = inst.getInt("m1");     // fewest steps in one move
    int m2 = inst.getInt("m2");     // most steps in one move
    int moves = n;                  // one move at most per step, so n moves cover any climb

    // steps[k]: steps taken at move k (0 when no move is made)
    IntVar[] steps = m.intVarArray("steps", moves, 0, m2);
    // pos[k]: height reached after k moves
    IntVar[] pos = m.intVarArray("pos", moves + 1, 0, n);

    // the climb starts on the ground
    pos[0].eq(0).post();

    for (int k = 0; k < moves; k++) {
      // a move takes m1 to m2 steps, or none once the top is reached
      steps[k].ge(m1).or(steps[k].eq(0)).post();

      // the height after a move is the height before it plus the steps taken
      m.sum(new IntVar[]{pos[k], steps[k]}, "=", pos[k + 1]).post();

      // no move is taken exactly when the top is already reached
      steps[k].eq(0).iff(pos[k].eq(n)).post();
    }

    // the climb ends exactly at the top of the stair
    pos[moves].eq(n).post();

    out.put("steps", steps);
  }
}
