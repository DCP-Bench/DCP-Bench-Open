:- lib(ic).
:- lib(branch_and_bound).
:- lib(timeout).

p_undef :- foo_bar(1), writeln(ok).
p_pow2 :- X #= 2^70, writeln(X).
p_ic_big :- X :: 0..3000000000, X #>= 2999999999, writeln(X).
p_bbcost :- X :: 1..5, bb_min(labeling([X]), X+1, bb_options{report_success:true/0}), writeln(X).
p_gvb :- X :: 1..9, X #> 3, get_var_bounds(X, L, H), writeln(L-H).
p_dom :- X :: 1..9, X #> 3, get_domain_as_list(X, L), writeln(L).
p_ic_float :- X :: 1..9, Y #= X/2, writeln(Y).
p_unbound_label :- X #> 3, labeling([X]), writeln(X).
p_ic_nolabel :- X :: 1..9, Y :: 1..9, X #= Y + 1, writeln(X-Y).
p_ic_imp :- X :: 1..9, B :: 0..1, B #= (X #> 5), writeln(B).
p_timeout :- timeout(repeat, 2, writeln(timed_out)).
p_timeout_ic :- length(L, 40), L :: 1..40, ( fromto(L,[Q|R],R,[]) do ( foreach(Q2,R), count(D,1,_), param(Q) do Q #\= Q2, Q #\= Q2+D, Q #\= Q2-D ) ), timeout(labeling(L), 2, writeln(timed_out)).
p_ic_gvb2 :- X :: 1..9, X #> 3, get_integer_bounds(X, L, H), writeln(L-H).
p_nth :- nth1(1, [a,b], X), writeln(X).
p_div :- X :: 1..9, Y #= X // 2, writeln(Y).
