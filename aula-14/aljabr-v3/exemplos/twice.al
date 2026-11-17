let twice = fn (f) => fn (x) => f(f(x)) in
twice(twice)(fn (x) => x * 2)(1)
