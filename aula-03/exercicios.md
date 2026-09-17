# Exercícios (Aula 03)

1. `q09` Escreva, no arquivo `parens.py` a função `parear_parens(expressao:
   str) -> bool` que determina se os parênteses em `expressao` estão corretamente pareados ou não. Não use pilha para implementar. Use apenas um contador.

2. `q10` Ajuste o código de `mlisp.py` para que detecte os erros sintáticos
   especificados nos arquivos de teste fornecidos (`test-*.py`).

3. `q11` Crie o interpretador `m2lisp.py` que permite e suporta operações de
   múltiplas aridades e também operações variádicas. As operações a serem suportadas são:

   `/`: binária (aridade é sempre 2); semântica: `(/ a b)` → a / b

   `-`: subtração pode ser unária e binária; com semântica:

         `(- a)`     →  -a
         `(- a b)`   →  a - b

   `+`: a adição é variádica; veja a semântica de algumas expressões

         `(+)`         →  0
         `(+ a)`       →  a
         `(+ a b)`     →  a + b
         `(+ a b c)`   →  a + b + c

   `*`: semelhante a `+`, mas com `(*)` → 1

4. `q12` No arquivo `sintaxe.md`, explique o que são a sintaxe concreta e a
   sintaxe abstrata. Como esses dois conceitos se manifestam nos
   interpretadores que escrevemos hoje em sala de aula?
