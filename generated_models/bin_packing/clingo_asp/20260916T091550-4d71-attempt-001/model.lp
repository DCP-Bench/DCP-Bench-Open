% Bin packing: assign each item to a bin without overloading any bin.
item(I) :- weights(I,_).
bin(0..B-1) :- num_bins(B).

1 { bins(I,B) : bin(B) } 1 :- item(I).

% Each bin carries at most its capacity. The reference ranges this over the
% item count rather than the bin count, but no item can be assigned outside
% 0..num_bins-1, so those extra indices constrain nothing.
:- capacity(C), bin(B), #sum { W,I : bins(I,B), weights(I,W) } > C.

#show bins/2.
