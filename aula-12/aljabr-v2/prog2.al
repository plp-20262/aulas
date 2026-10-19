let x = 2 in
let y = x ** 2 in
let f = [x, y => x + y] in
let z = f(x, y) in
x + y + z

