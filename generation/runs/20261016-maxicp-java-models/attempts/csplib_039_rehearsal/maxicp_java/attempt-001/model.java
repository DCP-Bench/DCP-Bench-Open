// Rehearsal ordering (CSPLib 039). The pieces of a concert are rehearsed one
// after another in slots. A player arrives immediately before the first piece
// they are in and leaves immediately after the last one. The waiting time of a
// player is the time they are present but not playing. Find the rehearsal
// order that minimises the total waiting time of all players.
import java.util.Arrays;

import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    int n = inst.getInt("num_pieces");
    int np = inst.getInt("num_players");
    int[] dur = inst.getIntArray("duration");
    int[][] rehearsal = inst.getIntMatrix("rehearsal"); // rehearsal[p][k] = 1 if player p is in piece k

    int total = 0;
    for (int k = 0; k < n; k++) total += dur[k];
    int big = total + 1; // larger than any time point, used to switch off a slot for a player

    // rehearsal_order[i] = piece rehearsed in slot i; the pieces form a permutation
    CPIntVar[] order = m.intVarArray(n, 0, n - 1);
    m.cp().post(allDifferent(order));

    // duration of the piece played in slot i
    CPIntVar[] slotDur = new CPIntVar[n];
    for (int i = 0; i < n; i++) slotDur[i] = element(dur, order[i]);

    // start time of slot i: the sum of the durations of the slots before it
    CPIntVar[] slotStart = new CPIntVar[n];
    slotStart[0] = m.intVar(0, 0);
    for (int i = 1; i < n; i++) slotStart[i] = sum(Arrays.copyOf(slotDur, i));

    // waiting time = (departure - arrival) - time spent playing. The time spent playing is fixed by the
    // data, so minimising the sum of (departure - arrival) over all players minimises the total waiting time.
    CPIntVar[] spans = new CPIntVar[2 * np];
    int t = 0;
    for (int p = 0; p < np; p++) {
      int playTime = 0;
      for (int k = 0; k < n; k++) playTime += rehearsal[p][k] * dur[k];
      if (playTime == 0) continue; // a player who is in no piece does not attend

      // plays = 1 if player p is in the piece rehearsed in slot i
      CPIntVar[] arrival = new CPIntVar[n]; // start of slot i if p plays there, otherwise a large value
      CPIntVar[] departure = new CPIntVar[n]; // end of slot i if p plays there, otherwise a small value
      for (int i = 0; i < n; i++) {
        CPIntVar plays = element(rehearsal[p], order[i]);
        CPIntVar late = element(new int[]{big, 0}, plays); // big if absent, 0 if playing
        CPIntVar early = element(new int[]{-big, 0}, plays); // -big if absent, 0 if playing
        arrival[i] = sum(new CPIntVar[]{slotStart[i], late});
        departure[i] = sum(new CPIntVar[]{slotStart[i], slotDur[i], early});
      }
      // player p arrives at the start of their first piece and leaves at the end of their last piece
      spans[t++] = max(departure);
      spans[t++] = minus(minimum(arrival));
    }

    m.minimize(sum(Arrays.copyOf(spans, t))); // the playing time is a constant, so it is left out
    out.put("rehearsal_order", order);
  }
}
