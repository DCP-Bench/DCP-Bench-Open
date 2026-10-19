% Session 3 Exodus puzzle: five children at Hebrew school (Bernice, Carl, Debby,
% Sammy, Ted) each told one part of the Exodus story (burning bush, captivity,
% Moses's youth, Passover, Ten Commandments). Each child is a different age
% (three, five, seven, eight, ten), and each family came from a different country
% (Ethiopia, Kazakhstan, Lithuania, Morocco, Yemen). Determine the association
% Age-Child-Country-Story.
%
% Encoding: ages, children, countries and stories are permutations of 1..5. A value
% is the row number shared by the four categories. Position k of a list is the k-th
% value of that category in the order of the description. For each child, AI, CI and
% SI give the age, country and story slot, and AV gives the age value.

:- lib(ic).

model(_Instance, Vars, [ages-Ag, children-Ch, countries-Co, stories-St]) :-
    % Numbers: the children are numbered 1..5 in the order of the description
    % (children[0] corresponds to Bernice), so the numbers are the child positions.
    Ch = [1, 2, 3, 4, 5],
    % Each other category is a permutation of the same numbers 1..5.
    length(Ag, 5), Ag :: 1..5, alldifferent(Ag),
    length(Co, 5), Co :: 1..5, alldifferent(Co),
    length(St, 5), St :: 1..5, alldifferent(St),
    % Slot of each child in the age, country and story lists.
    length(AI, 5), AI :: 1..5, alldifferent(AI),
    length(CI, 5), CI :: 1..5, alldifferent(CI),
    length(SI, 5), SI :: 1..5, alldifferent(SI),
    % Age value of each child: three, five, seven, eight, ten.
    length(AV, 5), AV :: [3, 5, 7, 8, 10], alldifferent(AV),
    % The child's row number sits in the age, country and story list at that child's slot.
    ( foreach(A, AI), foreach(R, Ch), param(Ag) do element(A, Ag, R) ),
    ( foreach(C, CI), foreach(R, Ch), param(Co) do element(C, Co, R) ),
    ( foreach(S, SI), foreach(R, Ch), param(St) do element(S, St, R) ),
    % The age slot gives the age value.
    ( foreach(A, AI), foreach(V, AV) do element(A, [3, 5, 7, 8, 10], V) ),

    % Children in the order Bernice, Carl, Debby, Sammy, Ted.
    AV = [AB, _AC, _AD, AS, AT],
    CI = [_CB, _CC, CD, _CS, _CT],

    % Debby's family is from Lithuania.
    CD #= 3,

    % The child who told the story of the Passover is two years older than Bernice.
    ( foreach(S, SI), foreach(A, AV), param(AB) do
        (S #= 4) => (A #= AB + 2)
    ),

    % The child whose family is from Yemen is younger than the child from the Ethiopian family.
    ( foreach(C1, CI), foreach(A1, AV), param(CI, AV) do
        ( foreach(C2, CI), foreach(A2, AV), param(C1, A1) do
            ((C1 #= 5) and (C2 #= 1)) => (A1 #< A2)
        )
    ),

    % The child from the Moroccan family is three years older than Ted.
    ( foreach(C, CI), foreach(A, AV), param(AT) do
        (C #= 4) => (A #= AT + 3)
    ),

    % Sammy is three years older than the child who told the story of Moses's youth in the house of the Pharaoh.
    ( foreach(S, SI), foreach(A, AV), param(AS) do
        (S #= 3) => (AS #= A + 3)
    ),

    flatten([Ag, Ch, Co, St, AI, CI, SI, AV], Vars).
