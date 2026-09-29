% Traffic lights: a four-way junction has four vehicle lights V1..V4 and four
% pedestrian lights P1..P4. Pick a state for each so that every pair of
% neighbouring roads shows one of the safe combinations.
% lights(I, S): light I is in state S. Lights 0..3 are the vehicle lights
% (0 = red, 1 = red-yellow, 2 = green, 3 = yellow), lights 4..7 the pedestrian
% lights (0 = red, 1 = green), in the order V1..V4, P1..P4.
1 { lights(I,S) : S = 0..3 } 1 :- I = 0..3.
1 { lights(I,S) : S = 0..1 } 1 :- I = 4..7.

% Road I (0..3) and the next road (road 3 is followed by road 0) must show one of
% the safe combinations (V_i, P_i, V_{i+1}, P_{i+1}) listed in allowed_tuples.
safe(I) :- I = 0..3,
    allowed_tuples(K,0,A), allowed_tuples(K,1,B), allowed_tuples(K,2,C), allowed_tuples(K,3,D),
    lights(I,A), lights(4 + I,B), lights((I + 1) \ 4,C), lights(4 + (I + 1) \ 4,D).
:- I = 0..3, not safe(I).

#show lights/2.
