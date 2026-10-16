// Alphabet blocks: each block has num_sides letters, the blocks hold the alphabet letters
// (no Q or Z), and every word in the list must be spellable, meaning its letters sit on
// distinct blocks. dice[l] is the block that carries letter l of the alphabet string.
import org.chocosolver.solver.Model;
import org.chocosolver.solver.variables.IntVar;
import dcp.Instance;
import dcp.Outputs;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    String alphabet = inst.getString("alphabet");      // the letters on the blocks, in order
    int numBlocks = inst.getInt("num_blocks");
    int numSides = inst.getInt("num_sides");           // letters per block
    int numLetters = inst.getInt("num_letters");
    String[] words = inst.getStringArray("words_str");

    // dice[l]: block of letter l, between 0 and numBlocks - 1
    IntVar[] dice = m.intVarArray("dice", numLetters, 0, numBlocks - 1);

    // every block carries exactly num_sides letters
    int[] blocks = new int[numBlocks];
    IntVar[] perBlock = new IntVar[numBlocks];
    for (int b = 0; b < numBlocks; b++) {
      blocks[b] = b;
      perBlock[b] = m.intVar(numSides);
    }
    m.globalCardinality(dice, blocks, perBlock, true).post();

    // every word can be spelled: its letters are on distinct blocks
    for (String word : words) {
      IntVar[] onBlocks = new IntVar[word.length()];
      for (int p = 0; p < word.length(); p++) {
        int letter = alphabet.indexOf(word.charAt(p));
        onBlocks[p] = dice[letter];
      }
      m.allDifferent(onBlocks, "AC").post();
    }

    out.put("dice", dice);
  }
}
