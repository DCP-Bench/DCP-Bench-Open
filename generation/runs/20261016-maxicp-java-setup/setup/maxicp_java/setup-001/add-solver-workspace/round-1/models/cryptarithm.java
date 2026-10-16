import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import org.maxicp.cp.engine.core.CPIntVar;
import org.maxicp.cp.engine.core.CPSolver;
import org.maxicp.search.DFSearch;
import org.maxicp.search.SearchStatistics;
import org.maxicp.util.exception.InconsistencyException;
import static org.maxicp.cp.CPFactory.*;
import static org.maxicp.search.Searches.*;

// Assign distinct digits to letters so that the addends sum to the sum word.
public class Cryptarithm {
    public static void main(String[] args) throws Exception {
        var data = JsonParser.parseString(Files.readString(Path.of(args[0]))).getAsJsonObject();
        JsonArray addendsJson = data.getAsJsonArray("addends");
        String[] addends = new String[addendsJson.size()];
        for (int i = 0; i < addends.length; i++) addends[i] = addendsJson.get(i).getAsString();
        String sumWord = data.get("sum").getAsString();

        // one variable per distinct letter
        TreeMap<Character, Integer> index = new TreeMap<>();
        for (String w : addends) for (char c : w.toCharArray()) index.putIfAbsent(c, index.size());
        for (char c : sumWord.toCharArray()) index.putIfAbsent(c, index.size());
        int letters = index.size();

        CPSolver cp = makeSolver();
        try {
            CPIntVar[] digit = makeIntVarArray(cp, letters, 0, 9);
            // different letters get different digits
            cp.post(allDifferent(digit));
            // no word of more than one letter starts with 0
            for (String w : addends) if (w.length() > 1) cp.post(ge(digit[index.get(w.charAt(0))], 1));
            if (sumWord.length() > 1) cp.post(ge(digit[index.get(sumWord.charAt(0))], 1));

            // the weighted digit sum of a word: each letter times its place value
            List<CPIntVar> lhs = new ArrayList<>();
            for (String w : addends) addWord(w, digit, index, lhs);
            List<CPIntVar> rhs = new ArrayList<>();
            addWord(sumWord, digit, index, rhs);
            // the addends add up to the sum word
            cp.post(sum(lhs.toArray(new CPIntVar[0]), sum(rhs.toArray(new CPIntVar[0]))));

            int[] values = new int[letters];
            DFSearch search = makeDfs(cp, firstFailBinary(digit));
            search.onSolution(() -> {
                for (int i = 0; i < letters; i++) values[i] = digit[i].min();
            });
            SearchStatistics stats = search.solve(s -> s.numberOfSolutions() >= 1);
            if (stats.numberOfSolutions() == 0) {
                System.out.println("{\"status\": \"unsatisfiable\"}");
                return;
            }
            StringBuilder out = new StringBuilder("{\"digits\": {");
            boolean first = true;
            for (Map.Entry<Character, Integer> e : index.entrySet()) {
                if (!first) out.append(", ");
                first = false;
                out.append("\"").append(e.getKey()).append("\": ").append(values[e.getValue()]);
            }
            out.append("}}");
            System.out.println(out);
        } catch (InconsistencyException e) {
            System.out.println("{\"status\": \"unsatisfiable\"}");
        }
    }

    // adds digit * 10^place for each letter of the word, rightmost letter has place 0
    static void addWord(String word, CPIntVar[] digit, Map<Character, Integer> index, List<CPIntVar> terms) {
        int place = 1;
        for (int k = word.length() - 1; k >= 0; k--) {
            terms.add(mul(digit[index.get(word.charAt(k))], place));
            place *= 10;
        }
    }
}
