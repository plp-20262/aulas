# match apenas casa um valor a um "padrão" ou "forma"
match 5 {    # o valor a "casar" é 5
  0 => 1     # o primeiro padrão é 0, com o qual claramente 5 não casa
  _ => 2     # o segundo padrão é o irrefutável: todo valor casa
}

# -> o valor da expressão acima é, portanto, 2
