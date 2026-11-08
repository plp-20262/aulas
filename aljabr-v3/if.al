let verdade = fn (t, f) => t in
let falso = fn (t, f) => f in
let if = fn (cond, then, else) => cond(then, else) in
if(falso, 10 + 10, 20 + 20)

