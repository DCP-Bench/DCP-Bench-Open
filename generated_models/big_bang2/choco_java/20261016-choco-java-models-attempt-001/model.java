import org.chocosolver.solver.Model;
import org.chocosolver.solver.search.limits.FailCounter;
import org.chocosolver.solver.search.strategy.Search;
import org.chocosolver.solver.variables.BoolVar;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

// Five nontransitive dice (Rock, Paper, Scissors, Lizard, Spock), each with six faces
// valued 1..12, so that the dice beat each other as in Rock-Paper-Scissors-Lizard-Spock.
// A beats B when A has a strictly larger face than B in more than half of the 36 face pairs.
public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    // Dice indices from the statement: row 0 Rock, 1 Paper, 2 Scissors, 3 Lizard, 4 Spock.
    final int ROCK = 0, PAPER = 1, SCISSORS = 2, LIZARD = 3, SPOCK = 4;
    final int DICE = 5, FACES = 6, MIN_FACE = 1, MAX_FACE = 12;
    final int PAIRS = FACES * FACES;   // 36 pairs of faces
    final int NEEDED = PAIRS / 2 + 1;  // more than half of the pairs: 19

    // each face value between 1 and 12 inclusive; repeats are allowed
    IntVar[][] dice = m.intVarMatrix("dice", DICE, FACES, MIN_FACE, MAX_FACE);

    // the order of faces on one die does not change any beats relation, so faces are
    // listed in nondecreasing order to remove that symmetry
    for (int d = 0; d < DICE; d++) {
      m.increasing(dice[d], 0).post();
    }

    // beats relationships as (winner, loser)
    int[][] beats = {
        {ROCK, SCISSORS}, {ROCK, LIZARD},
        {PAPER, ROCK}, {PAPER, SPOCK},
        {SCISSORS, PAPER}, {SCISSORS, LIZARD},
        {LIZARD, PAPER}, {LIZARD, SPOCK},
        {SPOCK, ROCK}, {SPOCK, SCISSORS}
    };

    for (int[] rel : beats) {
      int w = rel[0], l = rel[1];
      // the winner has a strictly larger face in more than half of all face pairs
      BoolVar[] larger = new BoolVar[PAIRS];
      int k = 0;
      for (int i = 0; i < FACES; i++) {
        for (int j = 0; j < FACES; j++) {
          larger[k++] = m.arithm(dice[w][i], ">", dice[l][j]).reify();
        }
      }
      m.sum(larger, ">=", NEEDED).post();
    }

    // search: branch on the faces of all dice, most constrained first, with restarts
    IntVar[] faces = new IntVar[DICE * FACES];
    for (int d = 0; d < DICE; d++) {
      for (int f = 0; f < FACES; f++) faces[d * FACES + f] = dice[d][f];
    }
    m.getSolver().setSearch(Search.domOverWDegSearch(faces));
    m.getSolver().setLubyRestart(50, new FailCounter(m, 1), 10000);

    out.put("dice", dice);
  }
}
