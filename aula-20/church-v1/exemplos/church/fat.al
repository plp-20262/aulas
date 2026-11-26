letrec fat = fn (n: Num) : Num =>
  if n == 0 then 1 else n * fat(n - 1)
in
fat(6)
