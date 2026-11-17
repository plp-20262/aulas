type Lista = Vazia | Cons(cabeca, cauda)

letrec tamanho = fn (xs) =>
  match xs {
    Vazia       => 0
    Cons(_, r)  => 1 + tamanho(r)
  }
in tamanho(Cons(1, Cons(2, Cons(3, Vazia))))
