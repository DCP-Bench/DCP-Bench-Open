% Every way to split the numbers 1..8 into two groups of four whose
% sums are equal (both 18). Each split appears twice: once with each
% group as "left". Run with -a to enumerate all of them.
int: n = 8;
int: half = n div 2;
int: target = n * (n + 1) div 4;

array[1..n] of var bool: left;   % true = the number is in the left group

constraint sum(i in 1..n)(bool2int(left[i])) = half;
constraint sum(i in 1..n)(i * bool2int(left[i])) = target;

solve satisfy;

output ["left group: ", show([i | i in 1..n where left[i]]), "\n"];
