let compose = fn (f, g) => fn (x) => f(g(x)) in
let inc = fn (x) => x + 1 in
let dobro = fn (x) => x * 2 in
let f = compose(inc, dobro) in
let g = compose(dobro, inc) in
f(5) + g(5)
