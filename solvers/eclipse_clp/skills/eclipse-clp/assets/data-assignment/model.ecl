% Assignment problem with the instance read from a JSON file (lib(json)).
% The path is the first user argument, default data.json. Sizes come from
% the data and keys the model does not use are ignored.
%   eclipse.exe -f model.ecl -e main -- other.json
:- lib(ic).
:- lib(ic_global).
:- lib(branch_and_bound).
:- lib(json).
:- import alldifferent/1 from ic_global.

% While the -e goal runs, argv(all, L) is [ProgramPath | UserArguments],
% all strings.
data_file(File) :-
    argv(all, All),
    ( All = [_, File|_] -> true ; File = "data.json" ).

main :-
    data_file(File),
    open(File, read, S),
    json_read(S, {Members}, [names_as_atoms]),   % an object is {[key:Value, ...]}
    close(S),
    memberchk(cost:Rows, Members),               % other keys are skipped
    length(Rows, N),
    length(Task, N),                             % Task[i] = task of worker i
    Task :: 1..N,
    alldifferent(Task),
    ( foreach(T, Task), foreach(Row, Rows), foreach(C, Cs) do
        element(T, Row, C)                       % C = Row[T], 1-based
    ),
    Total #= sum(Cs),
    bb_min(search(Task, 0, first_fail, indomain_min, complete, []), Total,
           bb_options{report_success:true/0, report_failure:true/0}),
    printf("total %d, task %w\n", [Total, Task]).
