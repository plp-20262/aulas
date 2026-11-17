let verdade = fn (t, f) => t in
let falso = fn (t, f) => f in
let se = fn (cond, entao, senao) => cond(entao, senao) in
let a = 0 in
se(verdade, 1 + a, 2 + a)
