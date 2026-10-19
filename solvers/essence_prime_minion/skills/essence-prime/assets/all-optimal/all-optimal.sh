#!/bin/sh
# Every optimal solution: (1) solve with the objective and check the optimum is proven,
# (2) drop the objective line, pin the objective expression to the optimum, enumerate.
set -e
model=knapsack.eprime
param=data.param

# Pass 1: the optimum. The objective is an expression, so read it back through a variable.
sed 's/^maximising \(.*\)$/find best : int(0..1000000)\nmaximising best/' "$model" > pass1.eprime
printf ',\nbest = (%s)\n' "$(sed -n 's/^maximising //p' "$model")" >> pass1.eprime
savilerow pass1.eprime "$param" -run-solver -solutions-to-stdout > pass1.out
grep -q 'SolverTimeOut:0' "$param.info" || { echo "optimum not proven"; exit 1; }
best=$(sed -n 's/^letting best be //p' pass1.out)
[ -n "$best" ] || { echo "no solution"; exit 1; }
echo "optimum: $best"

# Pass 2: no objective, objective expression fixed (in parentheses), all solutions with -S0.
sed '/^maximising /d' "$model" > pass2.eprime
printf ',\n(%s) = %s\n' "$(sed -n 's/^maximising //p' "$model")" "$best" >> pass2.eprime
savilerow pass2.eprime "$param" -run-solver -all-solutions -S0 -solutions-to-stdout > pass2.out
grep -q 'SolverTimeOut:0' "$param.info" || echo "enumeration incomplete"
grep '^letting take be' pass2.out
echo "optimal solutions: $(grep -c '^letting take be' pass2.out)"
