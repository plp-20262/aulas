# define o tipo Lista com variantes: L_/0 (lista vazia) e Cons/2
type Lista  = L_ | Cons(cabeca, cauda)

# define o tipo Arvore com variantes: A_/0 (árvore vazia) e No/2
type Arvore = A_ | No(valor, esquerda, direita)

# define função (recursiva) concat(lista1, lista2)
letrec concat = fn (lista1, lista2) =>
  match lista1 {
    L_                  => lista2
    Cons(cabeca, resto) => Cons(cabeca, concat(resto, lista2))
  } in

# define função em_ordem(arvore)
letrec em_ordem = fn (arvore) =>
  match arvore {               # se arvore …
    A_                  => L_  # … casa com o padrão A_ (é vazia)
    No(valor, esq, dir) =>     # … casa com o padrão No()
      let lista_esq = em_ordem(esq) in
      let lista_dir = em_ordem(dir) in
      concat(concat(lista_esq, Cons(valor, L_)), lista_dir)
  } in

#                   5
#                  / \
#                 3   6
# arvore =       / \
#               2   4
#              /
#             1
let arvore = No(5, No(3, No(2, No(1, A_, A_), A_), No(4, A_, A_)), No(6, A_, A_)) in
em_ordem(arvore)

# alternativas para testar também
#let arvore = No(2, No(1, A_, A_), No(3, A_, A_)) in
#let arvore = No(3, No(2, No(1, A_, A_), A_), A_) in
#let arvore = No(3, No(2, No(1, A_, A_), A_), No(4, A_, A_)) in
#let arvore = No(5, No(3, No(2, No(1, A_, A_), A_), No(4, A_, A_)), A_) in
