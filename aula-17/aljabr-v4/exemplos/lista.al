# define o tipo Lista com as variantes: Vazia/0 e Cell/2
type Lista = Vazia | Cell(cabeca, cauda)

# define l como a lista [1, 2, 3]
let l1 = Cell(2, Cell(3, Vazia)) in
let l = Cell(1, l1) in

# mostra l como resultado
l

# Use opção `-p` para ver o literal da lista
