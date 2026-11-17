type Lista = Vazia | Cons(cabeca, cauda)

letrec len = fn (lista) =>
  match lista {
    Vazia       => 0
    Cons(_, r)  => 1 + len(r)
  }
in 

let lista = Cons(50, Cons(10, Cons(30, Cons(0, Cons(20, Vazia))))) in
len(lista)
