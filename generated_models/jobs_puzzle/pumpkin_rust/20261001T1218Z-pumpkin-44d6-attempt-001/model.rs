// Jobs puzzle: four people (0..3) hold eight jobs, two each. From five clues,
// find the person holding each job.
//
// The instance has no fields: the people, the jobs and the clues are the
// puzzle's own data, mirrored from the reference.
fn build(_inst: &Instance, solver: &mut Solver) -> Model {
    let num_people = 4;
    let names = ["chef", "guard", "nurse", "clerk", "police_officer", "teacher", "actor", "boxer"];
    let jobs: Vec<Var> = names.iter().map(|_| solver.new_bounded_integer(0, num_people - 1)).collect();
    let (chef, _guard, nurse, clerk, police_officer, teacher, _actor, boxer) =
        (jobs[0], jobs[1], jobs[2], jobs[3], jobs[4], jobs[5], jobs[6], jobs[7]);

    // Each person holds exactly two jobs.
    let two_each = solver.new_constraint_tag();
    let two = solver.new_bounded_integer(2, 2);
    for person in 0..num_people {
        let holds: Vec<Lit> = jobs
            .iter()
            .map(|&job| {
                let l = solver.new_literal();
                solver.add_constraint(pumpkin_solver::equals(vec![job], person, two_each)).reify(l);
                l
            })
            .collect();
        solver
            .add_constraint(pumpkin_solver::boolean_equals(vec![1; holds.len()], holds, two, two_each))
            .post();
    }

    // Two jobs held by different people.
    let differ = |solver: &mut Solver, p: Var, q: Var, tag| {
        solver.add_constraint(pumpkin_solver::not_equals(vec![p.scaled(1), q.scaled(-1)], 0, tag)).post();
    };
    // A job not held by a given person.
    let not_by = |solver: &mut Solver, job: Var, person: i32, tag| {
        solver.add_constraint(pumpkin_solver::not_equals(vec![job], person, tag)).post();
    };

    // 1. The nurse is not the teacher, the police officer or the clerk.
    let tag = solver.new_constraint_tag();
    for other in [teacher, police_officer, clerk] {
        differ(solver, nurse, other, tag);
    }
    // 2. The clerk is not the chef.
    let tag = solver.new_constraint_tag();
    differ(solver, clerk, chef, tag);
    // 3. Person 0 is not the boxer.
    let tag = solver.new_constraint_tag();
    not_by(solver, boxer, 0, tag);
    // 4. Person 3 is not the teacher, the police officer or the nurse.
    let tag = solver.new_constraint_tag();
    for job in [teacher, police_officer, nurse] {
        not_by(solver, job, 3, tag);
    }
    // 5. Person 0, the chef and the police officer went golfing together, so
    //    they are three different people.
    let tag = solver.new_constraint_tag();
    not_by(solver, chef, 0, tag);
    not_by(solver, police_officer, 0, tag);
    differ(solver, chef, police_officer, tag);

    let mut m = Model::new();
    for (k, name) in names.iter().enumerate() {
        m.put(name, jobs[k]);
    }
    m
}
