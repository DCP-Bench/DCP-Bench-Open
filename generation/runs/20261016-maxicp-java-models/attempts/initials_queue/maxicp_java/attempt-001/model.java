import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

// Ten people in a queue, each with initials: an alphabetically ordered pair of
// distinct letters from A to E (letters 0 to 4). The ten people have different
// initials, and no two people next to each other share a letter.
// The person at the front has initials BE, the next one CD, and the last one BD.
// Print the queue (queue) as 10 lists of 2 integers, from the front.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // each person is a pair (first letter, second letter), 0 to 4
    CPIntVar[][] queue = new CPIntVar[10][];
    for (int i = 0; i < 10; i++) {
      queue[i] = m.intVarArray(2, 0, 4);
    }

    // each pair of initials is alphabetically ordered and the letters are distinct
    for (int i = 0; i < 10; i++) {
      // initials are an alphabetically ordered pair of distinct letters
      m.cp().post(le(queue[i][0], queue[i][1]));
      m.cp().post(neq(queue[i][0], queue[i][1]));
    }

    // all ten people have different initials
    CPIntVar[] codes = new CPIntVar[10];
    for (int i = 0; i < 10; i++) {
      // the pair is encoded as 5 times the first letter plus the second letter
      codes[i] = sum(mul(queue[i][0], 5), queue[i][1]);
    }
    // none of the people had the same initials as any other
    m.cp().post(allDifferent(codes));

    // no-one shared a letter with the person in front of them
    for (int i = 0; i < 9; i++) {
      for (int a = 0; a < 2; a++) {
        for (int b = 0; b < 2; b++) {
          m.cp().post(neq(queue[i][a], queue[i + 1][b]));
        }
      }
    }

    // Mathematician BE was at the front of the queue
    m.cp().post(eq(queue[0][0], 1));
    m.cp().post(eq(queue[0][1], 4));
    // with CD right behind
    m.cp().post(eq(queue[1][0], 2));
    m.cp().post(eq(queue[1][1], 3));
    // BD was right at the end of the queue
    m.cp().post(eq(queue[9][0], 1));
    m.cp().post(eq(queue[9][1], 3));

    out.put("queue", queue);
  }
}
