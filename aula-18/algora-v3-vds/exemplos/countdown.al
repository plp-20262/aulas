# define conta de forma recursiva
def conta(n) {
  if n == 0 {
    0
  } else {
    conta(n - 1)
  }
}

# invoca conta
conta(100)

# Lembre que a linguagem só mostra o significado da expressão,
# não os valores intermediários. Em breve, adicionamos um comando `print`.
# -> 0
