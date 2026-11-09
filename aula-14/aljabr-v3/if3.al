let verdade = fn (t, f) => t in
let falso = fn (t, f) => f in
let se = fn (cond, thunk_entao, thunk_senao) => cond(thunk_entao, thunk_senao)() in
let a = 0 in
se(verdade, fn () => 1 + a, fn () => 2 / a)
