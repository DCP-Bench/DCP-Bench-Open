import java.nio.file.*;
import java.util.*;
import org.jacop.core.*;
import org.jacop.constraints.*;
import org.jacop.search.*;
import org.json.*;

public class Cryptarithm {
    public static void main(String[] args) throws Exception {
        JSONObject data = new JSONObject(Files.readString(Path.of(args[0])));
        JSONArray ad = data.getJSONArray("addends");
        List<String> words = new ArrayList<>();
        for (int i = 0; i < ad.length(); i++) words.add(ad.getString(i));
        String sum = data.getString("sum");
        LinkedHashMap<Character, Integer> coef = new LinkedHashMap<>();
        Set<Character> leading = new HashSet<>();
        List<String> all = new ArrayList<>(words); all.add(sum);
        for (int wi = 0; wi < all.size(); wi++) {
            String s = all.get(wi);
            int sign = wi < words.size() ? 1 : -1;
            int p = 1;
            for (int k = s.length() - 1; k >= 0; k--) {
                coef.merge(s.charAt(k), sign * p, Integer::sum);
                p *= 10;
            }
            if (s.length() > 1) leading.add(s.charAt(0));
        }
        List<Character> letters = new ArrayList<>(coef.keySet());
        int m = letters.size();
        if (m > 10) { System.out.println("{\"status\": \"unsatisfiable\"}"); return; }
        Store store = new Store();
        IntVar[] x = new IntVar[m];
        int[] w = new int[m];
        for (int i = 0; i < m; i++) {
            char ch = letters.get(i);
            x[i] = new IntVar(store, String.valueOf(ch), leading.contains(ch) ? 1 : 0, 9);
            w[i] = coef.get(ch);
        }
        store.impose(new Alldistinct(x));
        store.impose(new LinearInt(x, w, "==", 0));
        DepthFirstSearch<IntVar> search = new DepthFirstSearch<>();
        search.setPrintInfo(false);
        search.setTimeOut(50);
        boolean found = search.labeling(store, new SimpleSelect<>(x, new SmallestDomain<>(), new IndomainMin<>()));
        if (found) {
            JSONObject d = new JSONObject();
            for (int i = 0; i < m; i++) d.put(String.valueOf(letters.get(i)), x[i].value());
            System.out.println(new JSONObject().put("digits", d));
        } else if (!search.timeOutOccured) System.out.println("{\"status\": \"unsatisfiable\"}");
        else System.err.println("timeout");
    }
}
