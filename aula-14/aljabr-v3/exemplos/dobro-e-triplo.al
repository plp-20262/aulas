let dobro = fn(x) => x * 2 in
let inc = fn(x) => x + 1 in

inc(inc(dobro(2)))
