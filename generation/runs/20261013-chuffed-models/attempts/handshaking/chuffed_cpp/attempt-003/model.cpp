// Handshaking: Hilary and Jocelyn host num_couples invited couples. Nobody shakes hands with self or spouse, and the hand counts of all people except Jocelyn are different. Print how many hands Hilary shook.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int num_couples = instance.at("num_couples");

  // person 0 is Hilary, person 1 is Jocelyn (the hosts, a married couple), and persons 2k and 2k+1 are the k-th invited couple
  int people = 2 * num_couples + 2;

  // couple[p] is the couple of person p; the hosts are couple 0
  std::vector<int> couple(people);
  for (int p = 0; p < people; ++p) couple[p] = (p < 2) ? 0 : p / 2;

  // shake[i][j] is 1 when persons i and j shake hands; the relation is symmetric, and spouses never shake hands
  vec<vec<IntVar*>> shake;
  shake.growTo(people);
  for (int i = 0; i < people; ++i) shake[i].growTo(people, getConstant(0));
  vec<IntVar*> decisions;
  for (int i = 0; i < people; ++i) {
    for (int j = i + 1; j < people; ++j) {
      if (couple[i] == couple[j]) continue;
      IntVar* h = newIntVar(0, 1);
      shake[i][j] = h;
      shake[j][i] = h;
      decisions.push(h);
    }
  }

  // hands[i] is the number of hands person i has shaken: the sum of his or her handshakes
  vec<IntVar*> hands;
  vec<int> ones;
  for (int i = 0; i < people; ++i) {
    vec<IntVar*> row;
    vec<int> coef;
    for (int j = 0; j < people; ++j) {
      if (j == i || couple[i] == couple[j]) continue;
      row.push(shake[i][j]);
      coef.push(1);
    }
    IntVar* h = newIntVar(0, people - 2);
    int_linear(coef, row, IRT_EQ, h);
    hands.push(h);
  }

  // all the answers are different, but Jocelyn does not answer, so her count is left out
  vec<IntVar*> answers;
  for (int i = 0; i < people; ++i) {
    if (i == 1) continue;
    answers.push(hands[i]);
  }
  all_different(answers);

  // the answers are 2n+1 different values from 0 to 2n, so they are exactly 0 to 2n and their sum is 0 + 1 + ... + 2n
  vec<int> answer_ones;
  for (int i = 0; i < answers.size(); ++i) answer_ones.push(1);
  int_linear(answer_ones, answers, IRT_EQ, num_couples * (2 * num_couples + 1));

  // the handshakes between two people are the decisions, searched in order
  branch(decisions, VAR_INORDER, VAL_MIN);

  outputs = {{"hil", dcp::out(hands[0])}};
}
