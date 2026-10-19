// Choose exactly two of five tasks with the smallest total cost, and list every such choice.
use std::ops::ControlFlow;
use std::time::Duration;

use pumpkin_solver::conflict_resolvers::resolvers::ResolutionResolver;
use pumpkin_solver::core::DefaultBrancher;
use pumpkin_solver::core::optimisation::OptimisationDirection;
use pumpkin_solver::core::optimisation::linear_sat_unsat::LinearSatUnsat;
use pumpkin_solver::core::predicates::Predicate;
use pumpkin_solver::core::results::{OptimisationResult, ProblemSolution, SatisfactionResult, SolutionReference};
use pumpkin_solver::core::termination::TimeBudget;
use pumpkin_solver::core::variables::TransformableVariable;
use pumpkin_solver::Solver;

fn main() {
    let costs = [3, 1, 2, 2, 5];

    let mut solver = Solver::default();
    let pick: Vec<_> = costs.iter().map(|_| solver.new_literal()).collect();
    let two = solver.new_bounded_integer(2, 2);
    let total = solver.new_bounded_integer(0, costs.iter().sum());

    // Exactly two picks: the weighted sum of picks, with unit weights, equals `two`.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(vec![1; costs.len()], pick.clone(), two, tag))
        .post();
    // The cost of the picks equals `total`.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(costs.to_vec(), pick.clone(), total, tag))
        .post();

    let mut brancher = solver.default_brancher();
    let mut resolver = ResolutionResolver::default();
    let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
    let procedure = LinearSatUnsat::new(
        OptimisationDirection::Minimise,
        total,
        |_: &Solver, _: SolutionReference, _: &DefaultBrancher, _: &ResolutionResolver| {
            ControlFlow::<()>::Continue(())
        },
    );
    let best = match solver.optimise(&mut brancher, &mut termination, &mut resolver, procedure) {
        OptimisationResult::Optimal(solution) => solution.get_integer_value(total),
        OptimisationResult::Unsatisfiable => {
            println!("no selection exists");
            return;
        }
        _ => {
            println!("optimality not proven");
            return;
        }
    };
    println!("minimum cost: {best}");

    // Hold the cost at its optimum and enumerate every selection that reaches it.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![total.scaled(1)], best, tag))
        .post();

    let mut count = 0;
    loop {
        let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
        let blocking: Vec<Predicate> = match solver.satisfy(&mut brancher, &mut termination, &mut resolver) {
            SatisfactionResult::Satisfiable(found) => {
                let solution = found.solution();
                count += 1;
                let chosen: Vec<usize> = pick
                    .iter()
                    .enumerate()
                    .filter(|(_, &p)| solution.get_integer_value(p) == 1)
                    .map(|(i, _)| i)
                    .collect();
                println!("optimal selection {count}: tasks {chosen:?}");
                pick.iter()
                    .map(|&p| {
                        if solution.get_integer_value(p) == 1 {
                            p.get_false_predicate()
                        } else {
                            p.get_true_predicate()
                        }
                    })
                    .collect()
            }
            SatisfactionResult::Unsatisfiable(..) => break,
            SatisfactionResult::Unknown(..) => {
                println!("time limit reached");
                return;
            }
        };
        let tag = solver.new_constraint_tag();
        solver.add_clause(blocking, tag);
    }
    println!("optimal solutions: {count}");
}
