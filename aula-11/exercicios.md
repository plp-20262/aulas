# Exercícios da Aula 11

Resolva antes da próxima aula.

1. Tokenize `(fn (x, y) => x + y)(2, 3)`.

2. Desenhe a árvore de sintaxe abstrata de `fn (x) => x + 1 (2)` e de
   `-f(2) ** 2`. O que você observa na primeira? O que acontece quando essa
   lambda é aplicada a um argumento?

3. Qual o resultado do programa abaixo? Explique como o resultado é obtido, com
   base na semântica informal, intencional que especificamos.

   ```text
   ```

4. Para cada programa abaixo, diga o resultado e justifique com base nas
   regras:

   ```text
   a) let a = 10 in
      let f = fn (x) => x + a in
      f(5)

   b) let x = 1 in
      let f = fn (y) => x + y in
      let g = fn (x) => f(x) in
      g(10)

   c) let x = 10 in (fn (x) => x + 1)(5)

   d) let make = fn (n) => fn (x) => x + n in
      let soma5 = make(5) in
      soma5(3)

   e) let f = fn (n) => f(n) in f(1)
   ```

5. **(Desafio)** Qual o resultado do programa abaixo? Faça a derivação das
   primeiras aplicações. O que há de diferente em relação aos exemplos da
   aula?

   ```text
   let aplica2 = fn (f, v) => f(f(v)) in
   aplica2(fn (x) => x * x, 3)
   ```

6. **(Desafio)** No exercício 4e, o programa dá erro porque `f` não está no
   ambiente do closure. O que precisaria mudar na regra (Let) para que `f`
   pudesse enxergar a si mesma? Que problema aparece ao tentar descrever o
   ambiente de criação desse closure? (Dica: o closure precisaria conter um
   ambiente que contém o próprio closure.)

7. **(Desafio extra)** O lexer de `aljabr` já reconhece o token `?` (entrada de
   dados), mas o parser ainda não o aceita. Estenda a gramática EBNF desta aula
   para incluí-lo e decida onde ele deve ficar na hierarquia de precedência.


