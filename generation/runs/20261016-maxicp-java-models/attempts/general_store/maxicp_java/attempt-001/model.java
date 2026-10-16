import org.maxicp.cp.engine.core.CPIntVar;
import static org.maxicp.cp.CPFactory.*;
import dcp.Instance;
import dcp.Model;
import dcp.Outputs;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// General store puzzle: each letter stands for a different digit, and the words
// above the line add up to ALL WOOL. Find the digit for each letter.
public class Submission {

  // The letters of the puzzle, in output order.
  static final String LETTERS = "ABCEHLOPSW";

  // Adds sign * (place value) of each letter of the word to the coefficient of that letter.
  static void addWord(Map<Character, Integer> coef, String word, int sign) {
    long place = 1;
    for (int i = word.length() - 1; i >= 0; i--) {
      char c = word.charAt(i);
      coef.merge(c, (int) (sign * place), Integer::sum);
      place *= 10;
    }
  }

  public static void build(Instance inst, Model m, Outputs out) {
    // Each letter is a digit from 0 to 9.
    Map<Character, CPIntVar> digit = new HashMap<>();
    CPIntVar[] all = new CPIntVar[LETTERS.length()];
    for (int i = 0; i < LETTERS.length(); i++) {
      all[i] = m.intVar(0, 9);
      digit.put(LETTERS.charAt(i), all[i]);
    }

    // Each different letter stands for a different digit.
    m.cp().post(allDifferent(all));

    // The words above the horizontal line add to ALL WOOL.
    String[] addends = {
      "CHESS", "CASH", "BOWWOW", "CHOPS", "ALSOPS", "PALEALE", "COOL", "BASS",
      "HOPS", "ALES", "HOES", "APPLES", "COWS", "CHEESE", "CHSOAP", "SHEEP"
    };
    Map<Character, Integer> coef = new HashMap<>();
    for (String w : addends) {
      addWord(coef, w, 1);
    }
    addWord(coef, "ALLWOOL", -1);

    // Split the weighted letters into the addends side and the total side, then
    // require both sides to be equal.
    List<CPIntVar> lhs = new ArrayList<>();
    List<CPIntVar> rhs = new ArrayList<>();
    for (Map.Entry<Character, Integer> e : coef.entrySet()) {
      int k = e.getValue();
      CPIntVar x = digit.get(e.getKey());
      if (k > 0) lhs.add(mul(x, k));
      else if (k < 0) rhs.add(mul(x, -k));
    }
    m.cp().post(eq(sum(lhs.toArray(new CPIntVar[0])), sum(rhs.toArray(new CPIntVar[0]))));

    for (int i = 0; i < LETTERS.length(); i++) {
      char c = LETTERS.charAt(i);
      out.put(String.valueOf(c), digit.get(c));
    }
  }
}
