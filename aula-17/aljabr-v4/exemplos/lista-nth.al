type Lista = Vazia | No(cabeca, cauda)

let erro = fn () => 1/0 in
letrec nth = fn (lista, n) =>
  match lista {
    Vazia => erro()
    No(cabeca, cauda) =>
      if n < 0
        then erro()
      else if n == 0
        then cabeca
      else
        nth(cauda, n - 1)
  }
in nth(No(0, No(10, No(20, No(30, Vazia)))), 2)
