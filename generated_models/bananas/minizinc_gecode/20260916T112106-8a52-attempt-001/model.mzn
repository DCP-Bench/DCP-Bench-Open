% Bananas: buy exactly 100 fruits for exactly 100 dollars, taking as few
% bananas and apples as possible. Multiplying by 3*5*7*9 = 945 clears the
% divisions, which is what the reference does.
var 1..100: bananas; var 1..100: oranges;
var 1..100: mangoes; var 1..100: apples;
var 1..2000: the_sum;

constraint the_sum = bananas + apples;
constraint 3 * bananas * 189 + 5 * oranges * 135
         + 7 * mangoes * 105 + 9 * apples * 315 = 100 * 945;
constraint bananas + oranges + mangoes + apples = 100;

var int: objective = the_sum;
solve minimize objective;

output ["{\"bananas\": ", show(bananas), ", \"oranges\": ", show(oranges),
        ", \"mangoes\": ", show(mangoes), ", \"apples\": ", show(apples), "}"];
