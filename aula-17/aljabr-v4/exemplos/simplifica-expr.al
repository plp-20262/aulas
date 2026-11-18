# Define o tipo Expr com variantes: Num/1, Add/2 e Mul/2
type Expr = Num(n) | Add(esq, dir) | Mul(esq, dir)

# Define a função simplifica(expr)
let simplifica = fn (expr) =>
  match expr {
    Add(Num(0), x)   => x
    Add(x, Num(0))   => x

    Mul(Num(1), x)   => x
    Mul(x, Num(1))   => x

    Mul(Num(0), _)   => Num(0)
    Mul(_, Num(0))   => Num(0)

    _                => expr
  }
in simplifica(Mul(Num(7), Num(0)))
