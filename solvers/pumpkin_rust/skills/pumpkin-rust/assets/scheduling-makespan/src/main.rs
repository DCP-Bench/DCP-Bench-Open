// Three tasks on one machine: task 0 must finish before task 2 starts. Minimise the makespan.
use std::ops::ControlFlow;
use std::time::Duration;

use pumpkin_solver::conflict_resolvers::resolvers::ResolutionResolver;
use pumpkin_solver::core::DefaultBrancher;
use pumpkin_solver::core::optimisation::OptimisationDirection;
use pumpkin_solver::core::optimisation::linear_sat_unsat::LinearSatUnsat;
use pumpkin_solver::core::results::{OptimisationResult, ProblemSolution, SolutionReference};
use pumpkin_solver::core::termination::TimeBudget;
use pumpkin_solver::core::variables::TransformableVariable;
use pumpkin_solver::Solver;

fn main() {
    let durations = [3, 2, 2];
    let horizon: i32 = durations.iter().sum();

    let mut solver = Solver::default();
    let start: Vec<_> = durations.iter().map(|_| solver.new_bounded_integer(0, horizon)).collect();
    let makespan = solver.new_bounded_integer(0, horizon);

    // At most one task at a time: a cumulative resource of capacity 1, each task using 1 unit.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::cumulative(
            start.clone(),
            durations.to_vec(),
            vec![1; durations.len()],
            1,
            tag,
        ))
        .post();

    // Precedence: start[2] >= start[0] + durations[0].
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(
            vec![start[0].scaled(1), start[2].scaled(-1)],
            -durations[0],
            tag,
        ))
        .post();

    // Every task ends by the makespan: start[i] + durations[i] <= makespan.
    for (i, &s) in start.iter().enumerate() {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![s.scaled(1), makespan.scaled(-1)],
                -durations[i],
                tag,
            ))
            .post();
    }

    let mut brancher = solver.default_brancher();
    let mut resolver = ResolutionResolver::default();
    let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
    let procedure = LinearSatUnsat::new(
        OptimisationDirection::Minimise,
        makespan,
        |_: &Solver, _: SolutionReference, _: &DefaultBrancher, _: &ResolutionResolver| {
            ControlFlow::<()>::Continue(())
        },
    );
    match solver.optimise(&mut brancher, &mut termination, &mut resolver, procedure) {
        OptimisationResult::Optimal(solution) => {
            let starts: Vec<i32> = start.iter().map(|&s| solution.get_integer_value(s)).collect();
            println!("makespan: {}", solution.get_integer_value(makespan));
            println!("start times: {starts:?}");
        }
        OptimisationResult::Unsatisfiable => println!("no schedule exists"),
        _ => println!("optimality not proven"),
    }
}
