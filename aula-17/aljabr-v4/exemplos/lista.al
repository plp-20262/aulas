# define o tipo Lista com as variantes: Vazia/0 e Cons/2
type Lista = Vazia | Cons(cabeca, cauda)

# define l como a lista [1, 2, 3]
let l = Cons(1, Cons(2, Cons(3, Vazia))) in

# mostra l como resultado
l

# Use opção `-p` para ver o literal da lista
