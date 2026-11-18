# define o tipo Lista com variantes: Vazia/0 e No/2
type Lista = Vazia | No(cabeca, cauda)

# define erro como uma função que produz erro (se invocada)
let erro = fn () => 1/0 in

# define nth(lista, n) que retorna n-ésimo elemento da lista (ou produz erro)
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
in

# define lista
let lista = No(10, No(20, No(30, No(40, Vazia)))) in

# qual o elemento de índice 2 de lista?
nth(lista, 2)

# -> 30
