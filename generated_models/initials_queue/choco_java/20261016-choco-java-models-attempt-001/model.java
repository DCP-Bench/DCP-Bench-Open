import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Initials queue: place ten people in a queue, each with a pair of distinct letters A..E
// (letters 0..4), so that the ten pairs are all different, no two neighbours share a letter,
// BE is at the front, CD right behind, and BD at the end.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int people = 10;
    int letters = 5;

    // queue[i][0] and queue[i][1] are the two letters of the person at position i,
    // with the first letter alphabetically before the second
    IntVar[][] queue = new IntVar[people][2];
    for (int i = 0; i < people; i++) {
      queue[i][0] = m.intVar("first" + i, 0, letters - 1);
      queue[i][1] = m.intVar("second" + i, 0, letters - 1);
      m.arithm(queue[i][0], "<", queue[i][1]).post();
    }

    // the pairs of initials are all different: code = 5 * first letter + second letter
    IntVar[] code = new IntVar[people];
    for (int i = 0; i < people; i++) {
      code[i] = queue[i][0].mul(letters).add(queue[i][1]).intVar();
    }
    m.allDifferent(code, "AC").post();

    // no-one shares a letter with the person in front of them
    for (int i = 0; i + 1 < people; i++) {
      for (int a = 0; a < 2; a++) {
        for (int b = 0; b < 2; b++) {
          m.arithm(queue[i][a], "!=", queue[i + 1][b]).post();
        }
      }
    }

    // mathematician BE (letters 1 and 4) is at the front of the queue
    m.arithm(queue[0][0], "=", 1).post();
    m.arithm(queue[0][1], "=", 4).post();

    // CD (letters 2 and 3) is right behind
    m.arithm(queue[1][0], "=", 2).post();
    m.arithm(queue[1][1], "=", 3).post();

    // BD (letters 1 and 3) is right at the end of the queue
    m.arithm(queue[people - 1][0], "=", 1).post();
    m.arithm(queue[people - 1][1], "=", 3).post();

    out.put("queue", queue);
  }
}
