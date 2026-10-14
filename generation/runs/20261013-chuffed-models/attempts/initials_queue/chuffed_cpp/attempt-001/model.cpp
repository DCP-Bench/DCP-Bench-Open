// Initials queue: ten people with distinct alphabetically ordered initial pairs from A..E, neighbours sharing no letter.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  const int n_people = 10, n_letters = 5;  // from the statement: 10 people, letters A..E (0..4)
  const int A = 0, B = 1, C = 2, D = 3, E = 4;

  // queue[i][0], queue[i][1] are the two initials of the person at position i (0 is the front)
  vec<vec<IntVar*>> queue;
  createVars(queue, n_people, 2, 0, n_letters - 1, true);

  // initials are an alphabetically ordered pair of distinct letters
  for (int i = 0; i < n_people; ++i) int_rel(queue[i][0], IRT_LT, queue[i][1]);

  // none of the people has the same initials as any other: encode the pair as 5*first + second
  vec<IntVar*> code;
  for (int i = 0; i < n_people; ++i) {
    vec<int> w;
    w.push(n_letters);
    w.push(1);
    vec<IntVar*> pair;
    pair.push(queue[i][0]);
    pair.push(queue[i][1]);
    IntVar* c = newIntVar(0, n_letters * n_letters - 1);
    int_linear(w, pair, IRT_EQ, c);
    code.push(c);
  }
  all_different(code);

  // no-one shares a letter with the person in front of them
  for (int i = 0; i + 1 < n_people; ++i)
    for (int p = 0; p < 2; ++p)
      for (int q = 0; q < 2; ++q) int_rel(queue[i][p], IRT_NE, queue[i + 1][q]);

  // BE is at the front of the queue, with CD right behind
  int_rel(queue[0][0], IRT_EQ, B);
  int_rel(queue[0][1], IRT_EQ, E);
  int_rel(queue[1][0], IRT_EQ, C);
  int_rel(queue[1][1], IRT_EQ, D);
  // BD is at the end of the queue
  int_rel(queue[n_people - 1][0], IRT_EQ, B);
  int_rel(queue[n_people - 1][1], IRT_EQ, D);

  branch(code, VAR_INORDER, VAL_MIN);
  json out = json::array();
  for (int i = 0; i < n_people; ++i) {
    json person = json::array();
    person.push_back(dcp::out(queue[i][0]));
    person.push_back(dcp::out(queue[i][1]));
    out.push_back(person);
  }
  outputs = {{"queue", out}};
}
