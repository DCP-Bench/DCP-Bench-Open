% Rectangle packing: place rectangular items, without overlap, inside a bounding rectangle
% (total_x wide, total_y high) whose area is as small as possible. Positions start at 0.
% Instance facts: widths(I,W) and heights(I,H): size of item I.
item(I) :- widths(I,_).
sum_w(S) :- S = #sum { W,I : widths(I,W) }.
sum_h(S) :- S = #sum { H,I : heights(I,H) }.
max_w(M) :- M = #max { W : widths(_,W) }.
max_h(M) :- M = #max { H : heights(_,H) }.

% Positions use an order encoding: ge_x(I,X) holds when item I starts at column X or later
% (ge_y for rows). Every item lies inside the area, whose extent is at most the sum of all
% widths (heights), so an item of width W starts at a column no larger than sum_w - W; the
% reference bounds positions by sum_w, and this is the same bound once the item must fit.
% Order atoms propagate much better than one atom per position when the bounding box shrinks.
{ ge_x(I,X) : X = 1..S-W } :- widths(I,W), sum_w(S).
{ ge_y(I,Y) : Y = 1..S-H } :- heights(I,H), sum_h(S).
:- ge_x(I,X+1), not ge_x(I,X), X >= 1.
:- ge_y(I,Y+1), not ge_y(I,Y), Y >= 1.

% pos_x(I,X) / pos_y(I,Y): the column and row where item I starts.
pos_x(I,0) :- item(I), not ge_x(I,1).
pos_x(I,X) :- ge_x(I,X), not ge_x(I,X+1).
pos_y(I,0) :- item(I), not ge_y(I,1).
pos_y(I,Y) :- ge_y(I,Y), not ge_y(I,Y+1).

% Every item lies within the overall area: total_x is at least the start column plus the width of
% every item, total_y likewise, and each is at least the largest item (the reference's lower bound).
% ge_tx(X) holds when total_x >= X. Only these lower bounds are forced, so total_x is the
% smallest allowed value, which is what the minimised area needs.
ge_tx(M) :- max_w(M).
ge_ty(M) :- max_h(M).
ge_tx(W) :- widths(I,W).
ge_ty(H) :- heights(I,H).
ge_tx(X+W) :- ge_x(I,X), widths(I,W).
ge_ty(Y+H) :- ge_y(I,Y), heights(I,H).
ge_tx(X) :- ge_tx(X+1), X >= 1.
ge_ty(Y) :- ge_ty(Y+1), Y >= 1.
total_x(X) :- ge_tx(X), not ge_tx(X+1).
total_y(Y) :- ge_ty(Y), not ge_ty(Y+1).

% No overlap: for every pair, one item lies entirely left of, or entirely below, the other.
% left(A,B): item A ends at or before the column where item B starts; below(A,B): same for rows.
1 { left(A,B); left(B,A); below(A,B); below(B,A) } :- item(A), item(B), A < B.
% In order encoding, "B starts at least W after A" means: whenever A starts at X or later,
% B starts at X+W or later (an atom that does not exist stands for a position that is too far right).
:- left(A,B), widths(A,W), not ge_x(B,W).
:- left(A,B), widths(A,W), ge_x(A,X), not ge_x(B,X+W).
:- below(A,B), heights(A,H), not ge_y(B,H).
:- below(A,B), heights(A,H), ge_y(A,Y), not ge_y(B,Y+H).

% The area to minimise is total_x * total_y.
area(X*Y) :- total_x(X), total_y(Y).
#minimize { A : area(A) }.

% left/below are not determined by the positions (a pair can satisfy several), so project the
% enumeration onto the shown atoms to avoid repeating one answer once per choice of relation.
#project pos_x/2.
#project pos_y/2.
#project total_x/1.
#project total_y/1.

#show pos_x/2.
#show pos_y/2.
#show total_x/1.
#show total_y/1.
