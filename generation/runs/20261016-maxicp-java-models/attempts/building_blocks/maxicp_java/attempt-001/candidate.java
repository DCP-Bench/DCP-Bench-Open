// Building blocks: alphabet blocks, each with one letter on each side, so that
// the blocks contain every letter of the alphabet. By arranging the blocks, all
// words of the list can be spelled. dice[k] is the block that letter k is placed on.

import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import org.maxicp.cp.engine.core.CPBoolVar;
import org.maxicp.cp.engine.core.CPIntVar;

public class Submission {
  public static void build(Instance inst, Model m, Outputs out) {
    String alphabet = inst.getString("alphabet");
    int numLetters = inst.getInt("num_letters");
    int numBlocks = inst.getInt("num_blocks");
    int numSides = inst.getInt("num_sides");
    String[] words = inst.getStringArray("words_str");

    // dice[k] is the block that letter k is placed on, between 0 and num_blocks-1.
    CPIntVar[] dice = m.intVarArray(numLetters, 0, numBlocks - 1);

    // Each block has num_sides sides, one letter on each side.
    for (int b = 0; b < numBlocks; b++) {
      CPIntVar[] onBlock = new CPIntVar[numLetters];
      for (int k = 0; k < numLetters; k++) {
        onBlock[k] = isEq(dice[k], b);
      }
      m.cp().post(eq(sum(onBlock), numSides));
    }

    // Every word of the list can be spelled: its letters are on different blocks,
    // since one block shows one letter at a time.
    for (String word : words) {
      CPIntVar[] letterBlocks = new CPIntVar[word.length()];
      for (int p = 0; p < word.length(); p++) {
        letterBlocks[p] = dice[alphabet.indexOf(word.charAt(p))];
      }
      m.cp().post(allDifferent(letterBlocks));
    }

    out.put("dice", dice);
  }
}
