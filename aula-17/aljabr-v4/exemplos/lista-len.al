# define o tipo Lista com variantes: Vazia/0 e Cons/2
type Lista = Vazia | Cons(cabeca, cauda)

# define a função recursiva len(lista)
letrec len = fn (lista) =>
  match lista {                 # se lista … 
    Vazia       => 0            # … casa com Vazia
    Cons(_, r)  => 1 + len(r)   # … casa com Cons
  }
in 

let lista = Cons(50, Cons(10, Cons(30, Cons(0, Cons(20, Vazia))))) in
len(lista)
