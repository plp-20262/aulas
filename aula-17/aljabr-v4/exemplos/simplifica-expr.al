type Expr = Num(n) | Add(esq, dir) | Mul(esq, dir)

let simplifica = fn (e) =>
  match e {
    Add(Num(0), x)   => x
    Add(x, Num(0))   => x

    Mul(Num(1), x)   => x
    Mul(x, Num(1))   => x

    Mul(Num(0), _)   => Num(0)
    Mul(_, Num(0))   => Num(0)

    _                => e
  }
in simplifica(Mul(Num(7), Num(0)))
