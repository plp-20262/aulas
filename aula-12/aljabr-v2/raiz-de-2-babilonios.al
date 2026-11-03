let twice = fn (f) => fn (x) => f(f(x)) in
let passo = fn (x) => (x + 2 / x) / 2 in
twice(twice(twice(passo)))(1)
