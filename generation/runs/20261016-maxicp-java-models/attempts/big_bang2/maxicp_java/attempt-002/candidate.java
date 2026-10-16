// Nontransitive dice: five dice (Rock, Paper, Scissors, Lizard, Spock) with
// six faces each, valued 1..12, whose 'beats' relation follows the extended
// Rock-Paper-Scissors rules. A die beats another when it has a strictly larger
// face value than the other die in more than half of the 36 face pairs.

import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // row 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock
    int dice = 5;
    int faces = 6;

    // each die has six faces, each face value between 1 and 12
    CPIntVar[][] dice_ = new CPIntVar[dice][faces];
    for (int d = 0; d < dice; d++)
      for (int f = 0; f < faces; f++)
        dice_[d][f] = m.intVar(1, 12);

    // shifting every face value by the same amount keeps all beats relations,
    // so the lowest face value over all dice is taken to be 1 (symmetry break
    // that keeps every relation but the shift)
    CPBoolVar[] someOne = new CPBoolVar[dice * faces];
    int k0 = 0;
    for (int d = 0; d < dice; d++)
      for (int f = 0; f < faces; f++)
        someOne[k0++] = isEq(dice_[d][f], 1);
    m.cp().post(or(someOne));

    // the ten 'beats' relationships, as (winner, loser)
    // Rock crushes Scissors, Rock crushes Lizard
    // Paper covers Rock, Paper disproves Spock
    // Scissors cuts Paper, Scissors decapitate Lizard
    // Lizard eats Paper, Lizard poisons Spock
    // Spock vaporizes Rock, Spock smashes Scissors
    int[][] beats = {
      {0, 2}, {0, 3},
      {1, 0}, {1, 4},
      {2, 1}, {2, 3},
      {3, 1}, {3, 4},
      {4, 0}, {4, 2}
    };

    for (int[] b : beats) {
      CPIntVar[] winner = dice_[b[0]];
      CPIntVar[] loser = dice_[b[1]];
      // the winner has a strictly larger face than the loser in more than half
      // of the 36 face pairs, that is in at least 19 of them
      CPBoolVar[] larger = new CPBoolVar[faces * faces];
      int k = 0;
      for (int i = 0; i < faces; i++)
        for (int j = 0; j < faces; j++)
          // winner face > loser face, reified as not (winner face <= loser face)
          larger[k++] = not(isLe(winner[i], loser[j]));
      m.cp().post(ge(sum(larger), 19));
      // redundant: the loser wins in at most 36 - 19 = 17 of the face pairs
      CPBoolVar[] smaller = new CPBoolVar[faces * faces];
      k = 0;
      for (int i = 0; i < faces; i++)
        for (int j = 0; j < faces; j++)
          smaller[k++] = not(isLe(loser[j], winner[i]));
      m.cp().post(le(sum(smaller), 17));
    }

    out.put("dice", dice_);
  }
}
