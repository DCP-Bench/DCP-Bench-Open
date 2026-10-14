% Kidney exchange: n people wait for a kidney. Person i can donate to the people listed for i.
% Choose who donates to whom so that everyone who gives a kidney also receives one, nobody gives
% or receives more than one, and as many transplants as possible happen.
% Instance facts: num_people(N); compatible(I,K,J): J is the K-th person (numbered from 1) to
% whom person I (numbered from 0) can donate. A person with an empty list has no facts.
person(0..N-1) :- num_people(N).

% can_donate(I,J): person I can donate to person J (both numbered from 0; the list uses numbering from 1).
can_donate(I,J-1) :- compatible(I,_,J).

% donates(I,J): person I donates to person J, which is only possible for a compatible pair.
% idle(I): person I takes no part, neither giving nor receiving.
% Why every person is either idle or both gives and receives exactly once: anyone who gives must
% receive, and a person who received but gave nothing would need a giver that itself receives from
% another giver, and so on backwards, which can only close into a cycle that never reaches that
% person. So the exchanges are disjoint cycles, and "exactly one of give, idle" and "exactly
% one of receive, idle" describe them. This form lets the solver reason about each person's single
% gift and single kidney directly, instead of only counting "at most one".
1 { donates(I,J) : can_donate(I,J); idle(I) } 1 :- person(I).
1 { donates(I,J) : can_donate(I,J); idle(J) } 1 :- person(J).

% Maximise the number of transplants. Every person who takes part gives exactly one kidney, so the
% number of transplants is the number of people minus the idle ones, and maximising it is the same
% as minimising the idle people. Stated this way the solver can see at once that the best possible
% value is 0 idle people, which proves optimality as soon as everybody can be placed.
#minimize { 1,I : idle(I) }.

% transplants(I,J,true/false): whether person I donates to person J.
transplants(I,J,true)  :- donates(I,J).
transplants(I,J,false) :- person(I), person(J), not donates(I,J).

#show transplants/3.
