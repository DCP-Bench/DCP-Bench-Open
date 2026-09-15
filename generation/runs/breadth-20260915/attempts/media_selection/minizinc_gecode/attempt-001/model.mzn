include "globals.mzn";

array[int] of int: target_audiences;
array[int] of int: advertising_media;
array[int, int] of int: incidence_matrix;
array[int] of int: media_costs;

set of int: Audiences = 1..length(target_audiences);
set of int: Media = 1..length(advertising_media);
array[Media] of var bool: is_selected;

constraint forall(t in Audiences) (
    sum(m in Media) (incidence_matrix[t, m] * bool2int(is_selected[m])) >= 1);

var int: objective = sum(m in Media) (media_costs[m] * bool2int(is_selected[m]));
solve minimize objective;

output ["{\"is_selected\": [", join(", ", [show(is_selected[m]) | m in Media]),
        "], \"min_total_cost\": ", show(objective), "}"];
