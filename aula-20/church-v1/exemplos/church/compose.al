let compose = fn (f: (Num) -> Num, g: (Num) -> Num) =>
  fn (x: Num) => f(g(x))
in
let inc = fn (x: Num) => x + 1 in
let dobro = fn (x: Num) => x * 2 in
compose(inc, dobro)(10)
