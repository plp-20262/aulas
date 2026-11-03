let verdade = fn (t, f) => t in
let falso = fn (t, f) => f in
let not = fn (b) => b(falso, verdade) in
let and = fn (b1, b2) => b1(b2, falso) in
let or = fn (b1, b2) => b1(verdade, b2) in
let to_num = fn (b) => b(1, 0) in
to_num(and(verdade, verdade))
