// Enumerate every way to make 10 from coins of 1, 2 and 5.
use std::time::Duration;

use pumpkin_solver::conflict_resolvers::resolvers::ResolutionResolver;
use pumpkin_solver::core::predicates::{Predicate, PredicateConstructor};
use pumpkin_solver::core::results::{ProblemSolution, SatisfactionResult};
use pumpkin_solver::core::termination::TimeBudget;
use pumpkin_solver::core::variables::TransformableVariable;
use pumpkin_solver::Solver;

fn main() {
    let mut solver = Solver::default();
    let ones = solver.new_bounded_integer(0, 10);
    let twos = solver.new_bounded_integer(0, 5);
    let fives = solver.new_bounded_integer(0, 2);

    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![ones.scaled(1), twos.scaled(2), fives.scaled(5)],
            10,
            tag,
        ))
        .post();

    let mut brancher = solver.default_brancher();
    let mut resolver = ResolutionResolver::default();
    let mut count = 0;
    loop {
        let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
        // The result borrows the solver, so the blocking clause is built inside
        // the match and posted after it.
        let blocking: Vec<Predicate> = match solver.satisfy(&mut brancher, &mut termination, &mut resolver) {
            SatisfactionResult::Satisfiable(found) => {
                let solution = found.solution();
                count += 1;
                let (a, b, c) = (
                    solution.get_integer_value(ones),
                    solution.get_integer_value(twos),
                    solution.get_integer_value(fives),
                );
                println!("ones={a} twos={b} fives={c}");
                vec![
                    ones.disequality_predicate(a),
                    twos.disequality_predicate(b),
                    fives.disequality_predicate(c),
                ]
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
    println!("total solutions: {count}");
}
