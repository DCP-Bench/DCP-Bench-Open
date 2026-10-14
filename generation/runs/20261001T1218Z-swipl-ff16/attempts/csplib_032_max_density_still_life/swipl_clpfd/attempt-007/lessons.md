# Lessons (swipl_clpfd)

1. A disjunction used as a filter inside findall/3, for example
   `member(DI, [-1,0,1]), member(DJ, [-1,0,1]), (DI =\= 0 ; DJ =\= 0)`,
   succeeds twice for every pair where both tests hold, so the diagonal
   neighbours of a cell were listed twice and counted twice. Six attempts
   (attempt-001 to attempt-006) were rejected with invalid_solution for this
   one cause. Use `\+ (DI =:= 0, DJ =:= 0)`.
2. The last 4000 characters of the container's stderr are kept in
   evaluation.json (`instances[].stderr`). A goal such as
   `when(ground(Cells-Live), format(user_error, ...))` shows the grids the
   search reaches, which is how the cause above was found (attempt-006 does
   this and was never meant to be retained).
3. An auxiliary variable defined by `Bye #= 1 - Home - Away` has the domain
   -1..1; without `Bye in 0..1` a team can play two games a day
   (csplib_011, attempt-004, invalid_solution).
