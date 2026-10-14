#include <vector>
#include <nlohmann/json.hpp>
#include "ortools/sat/cp_model.h"

using nlohmann::json;
using namespace operations_research;
using namespace operations_research::sat;

// Jobs puzzle: four people (0-3) hold eight jobs, two each: chef, guard, nurse,
// clerk, police officer, teacher, actor and boxer. Assign each job a person
// from five clues.
// The problem has no instance data.
void Build(const json& /*instance*/, CpModelBuilder& model, json& outputs) {
  const int num_people = 4;
  const int num_jobs = 8;

  // jobs[j] is the person holding job j.
  std::vector<IntVar> jobs;
  for (int j = 0; j < num_jobs; ++j) jobs.push_back(model.NewIntVar(Domain(0, num_people - 1)));
  const IntVar &chef = jobs[0], &guard = jobs[1], &nurse = jobs[2], &clerk = jobs[3],
               &police_officer = jobs[4], &teacher = jobs[5], &actor = jobs[6], &boxer = jobs[7];

  // Each person holds exactly two jobs. holds[j][p] is reified both ways on
  // jobs[j] == p and counted per person.
  std::vector<LinearExpr> held(num_people);
  for (int j = 0; j < num_jobs; ++j) {
    for (int p = 0; p < num_people; ++p) {
      const BoolVar holds = model.NewBoolVar();
      model.AddEquality(jobs[j], p).OnlyEnforceIf(holds);
      model.AddNotEqual(jobs[j], p).OnlyEnforceIf(holds.Not());
      held[p] += holds;
    }
  }
  for (int p = 0; p < num_people; ++p) model.AddEquality(held[p], 2);

  // 1. The nurse is not the teacher, the police officer or the clerk.
  model.AddNotEqual(nurse, teacher);
  model.AddNotEqual(nurse, police_officer);
  model.AddNotEqual(nurse, clerk);

  // 2. The clerk is not the chef.
  model.AddNotEqual(clerk, chef);

  // 3. Person 0 is not the boxer.
  model.AddNotEqual(boxer, 0);

  // 4. Person 3 is not the teacher, the police officer or the nurse.
  model.AddNotEqual(teacher, 3);
  model.AddNotEqual(police_officer, 3);
  model.AddNotEqual(nurse, 3);

  // 5. Person 0, the chef and the police officer went golfing together, so they
  //    are three different people.
  model.AddNotEqual(chef, 0);
  model.AddNotEqual(police_officer, 0);
  model.AddNotEqual(chef, police_officer);

  outputs = {{"chef", chef.index()},       {"guard", guard.index()},
             {"nurse", nurse.index()},     {"clerk", clerk.index()},
             {"police_officer", police_officer.index()},
             {"teacher", teacher.index()}, {"actor", actor.index()},
             {"boxer", boxer.index()}};
}
