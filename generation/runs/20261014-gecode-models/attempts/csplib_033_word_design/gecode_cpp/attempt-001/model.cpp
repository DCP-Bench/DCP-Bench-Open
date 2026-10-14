#include "dcp.h"

// Word design: find a set of num_words words of length n over the alphabet
// {A, C, G, T}, coded 1, 2, 3, 4, such that every word has exactly four letters
// from {C, G}, every two distinct words differ in at least four positions, and
// for every pair x, y (x = y allowed) the reverse of x and the Watson-Crick
// complement of y differ in at least four positions.
class WordDesign : public dcp::Space {
 protected:
  int n;
  int num_words;
  IntVarArray letter;  // letter[w * n + k]: letter k of word w (1 = A, 2 = C, 3 = G, 4 = T)

  // letter k of word w
  IntVar at(int w, int k) const { return letter[w * n + k]; }

 public:
  explicit WordDesign(const json& instance) {
    n = instance.at("n").get<int>();
    num_words = instance.at("num_words").get<int>();
    letter = IntVarArray(*this, num_words * n, 1, 4);

    // each word has exactly four symbols from {C, G}
    for (int w = 0; w < num_words; ++w) {
      IntVarArgs row;
      for (int k = 0; k < n; ++k) row << at(w, k);
      count(*this, row, IntSet(2, 3), IRT_EQ, 4);
    }

    // two distinct words differ in at least four positions:
    // at most n - 4 positions where they agree
    for (int w = 0; w < num_words; ++w) {
      for (int v = w + 1; v < num_words; ++v) {
        BoolVarArgs agree;
        for (int k = 0; k < n; ++k) agree << expr(*this, at(w, k) == at(v, k));
        linear(*this, agree, IRT_LQ, n - 4);
      }
    }

    // for every pair x, y (x = y allowed), the reverse of x and the Watson-Crick
    // complement of y differ in at least four positions. The complement of a
    // letter c is 5 - c (A-T and C-G), so position k of the two words matches
    // when x[n-1-k] + y[k] == 5: at most n - 4 such positions.
    for (int w = 0; w < num_words; ++w) {
      for (int v = 0; v < num_words; ++v) {
        BoolVarArgs match;
        for (int k = 0; k < n; ++k) match << expr(*this, at(w, n - 1 - k) + at(v, k) == 5);
        linear(*this, match, IRT_LQ, n - 4);
      }
    }

    // the words form a set, so list them in lexicographic order
    for (int w = 0; w + 1 < num_words; ++w) {
      IntVarArgs first, second;
      for (int k = 0; k < n; ++k) {
        first << at(w, k);
        second << at(w + 1, k);
      }
      rel(*this, first, IRT_LQ, second);
    }

    branch(*this, letter, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    std::vector<IntVarArgs> words;
    for (int w = 0; w < num_words; ++w) {
      IntVarArgs row;
      for (int k = 0; k < n; ++k) row << at(w, k);
      words.push_back(row);
    }
    output("words", words);
  }

  WordDesign(WordDesign& s) : dcp::Space(s), n(s.n), num_words(s.num_words) {
    letter.update(*this, s.letter);
  }
  Gecode::Space* copy() override { return new WordDesign(*this); }
};

DCP_MODEL(WordDesign)
