// Permutation flow shop: every job goes through all machines in the same order
// (machine 1 first), and all machines process the jobs in the same sequence.
// Choose the sequence of jobs and the start times so that the time at which
// the last job finishes on the last machine (the makespan) is as small as possible.

type Tag = pumpkin_solver::core::proof::ConstraintTag;

// Post "exactly one of these literals is true".
fn exactly_one(solver: &mut Solver, lits: Vec<Lit>, tag: Tag) {
    let n = lits.len();
    solver.add_constraint(pumpkin_solver::clause(lits.clone(), tag)).post();
    solver
        .add_constraint(pumpkin_solver::boolean_less_than_or_equals(vec![1; n], lits, 1, tag))
        .post();
}

fn build(inst: &Instance, solver: &mut Solver) -> Model {
    let n_jobs = inst.len("jobs");
    let n_machines = inst.len("machines");
    let process_time = inst.matrix("process_time"); // process_time[j][m]: time of job j on machine m

    // No schedule can take longer than doing all the work one piece after another.
    let max_duration: i32 = process_time.iter().map(|row| row.iter().sum::<i32>()).sum();

    // at[k][j] is true when job j is the k-th job in the sequence. Every position
    // holds exactly one job and every job has exactly one position, so the
    // sequence is a permutation of the jobs (the reference's AllDifferent).
    let at: Vec<Vec<Lit>> = (0..n_jobs)
        .map(|_| (0..n_jobs).map(|_| solver.new_literal()).collect())
        .collect();
    let permutation = solver.new_constraint_tag();
    for k in 0..n_jobs {
        exactly_one(solver, at[k].clone(), permutation);
    }
    for j in 0..n_jobs {
        exactly_one(solver, (0..n_jobs).map(|k| at[k][j]).collect(), permutation);
    }

    // start_times[k][m] and end_times[k][m]: when the k-th job of the sequence
    // starts and finishes on machine m.
    let start_times: Vec<Vec<Var>> = (0..n_jobs)
        .map(|_| (0..n_machines).map(|_| solver.new_bounded_integer(0, max_duration)).collect())
        .collect();
    let end_times: Vec<Vec<Var>> = (0..n_jobs)
        .map(|_| (0..n_machines).map(|_| solver.new_bounded_integer(0, max_duration)).collect())
        .collect();

    let length = solver.new_constraint_tag();
    let after_previous_machine = solver.new_constraint_tag();
    let after_previous_job = solver.new_constraint_tag();
    for k in 0..n_jobs {
        for m in 0..n_machines {
            // The time the k-th job of the sequence needs on machine m is the
            // processing time of whichever job sits at position k:
            // end = start + sum over jobs j of process_time[j][m] * at[k][j].
            // Zero processing times are left out of the sum (Pumpkin cannot take
            // a zero coefficient).
            let mut terms: Vec<Term> = vec![end_times[k][m].scaled(1), start_times[k][m].scaled(-1)];
            for j in 0..n_jobs {
                if process_time[j][m] != 0 {
                    terms.push(at[k][j].get_integer_variable().scaled(-process_time[j][m]));
                }
            }
            solver
                .add_constraint(pumpkin_solver::equals(terms, 0, length))
                .post();

            // A job cannot start on machine m before it has finished on machine m - 1.
            if m > 0 {
                solver
                    .add_constraint(pumpkin_solver::less_than_or_equals(
                        vec![end_times[k][m - 1].scaled(1), start_times[k][m].scaled(-1)],
                        0,
                        after_previous_machine,
                    ))
                    .post();
            }
            // The k-th job cannot start on machine m before the (k-1)-th job has
            // finished on it.
            if k > 0 {
                solver
                    .add_constraint(pumpkin_solver::less_than_or_equals(
                        vec![end_times[k - 1][m].scaled(1), start_times[k][m].scaled(-1)],
                        0,
                        after_previous_job,
                    ))
                    .post();
            }
        }
    }

    // The makespan is the latest end time; it is minimised.
    let makespan = solver.new_bounded_integer(0, max_duration);
    let all_ends: Vec<Var> = end_times.iter().flatten().copied().collect();
    let latest = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::maximum(all_ends, makespan, latest))
        .post();

    let mut model = Model::new();
    model.put("makespan", makespan);
    model.minimise(makespan);
    model
}
