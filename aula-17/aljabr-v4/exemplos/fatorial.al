let verdade = fn (t, f) => t in
let falso = fn (t, f) => f in
let if = fn (cond, then, else) => cond(then, else) in
let fat = fn (n) => if(n == 0, 1, n * fat(n - 1)) in
fat(3)
