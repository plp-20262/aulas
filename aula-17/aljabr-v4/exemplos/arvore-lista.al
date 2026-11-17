type Arvore = A_ | No(valor, esquerda, direita)
type Lista  = L_ | Cons(cabeca, cauda)

letrec append = fn (lista1, lista2) =>
  match lista1 {
    L_         => lista2
    Cons(c, r) => Cons(c, append(r, lista2))
  } in

letrec inorder = fn (t) =>
  match t {
    A_          => L_
    No(v, e, d) =>
      let lista_esq = inorder(e) in
      let lista_dir = inorder(d) in
      append(append(lista_esq, Cons(v, L_)), lista_dir)
  } in

let arvore = No(5, No(3, No(2, No(1, A_, A_), A_), No(4, A_, A_)), A_) in
inorder(arvore)
