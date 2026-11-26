let twice = fn (f: (Num) -> Num) => fn (x: Num) => f(f(x)) in
twice(fn (n: Num) => n + 1)(0)
