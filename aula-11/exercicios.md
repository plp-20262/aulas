# Exercícios da Aula 11

Resolva antes da próxima aula.

1. `[q16]` Tokenize `(fn (x, y) => x + y)(2, 3)`.

2. `[q17]` Desenhe a árvore de sintaxe abstrata de `fn (x) => x + 1 (2)` e de
   `-f(2) ** 2`. O que você observa na primeira? O que acontece quando essa
   lambda é aplicada a um argumento?

3. Para cada programa abaixo, diga o resultado e justifique com base nas
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

4. `[q18]`**(Desafio)** Qual o resultado do programa abaixo? Faça a derivação
   das primeiras aplicações. O que há de diferente em relação aos exemplos da
   aula?

   ```text
   let aplica2 = fn (f, v) => f(f(v)) in
   aplica2(fn (x) => x * x, 3)
   ```

5. `[q19]` **(Desafio)** No exercício 3e, o programa dá erro porque `f` não
   está no ambiente do closure. O que precisaria mudar na regra (Let) para que
   `f` pudesse enxergar a si mesma? Que problema aparece ao tentar descrever o
   ambiente de criação desse closure? (Dica: o closure precisaria conter um
   ambiente que contém o próprio closure.)

6. `[q20]`**(Desafio extra)** O lexer de `aljabr` já reconhece o token `?`
   (entrada de dados), mas o parser ainda não o aceita. Estenda a gramática
   EBNF desta aula para incluí-lo e decida onde ele deve ficar na hierarquia de
   precedência.

7. `[q21]` Faça uma cópia completa do diretório de `aljabr-v1` para o diretório
   `q21/aljabr-v2` (atenção, o nome de versão deste diretório deve ser `v2`,
   mesmo você tendo que copiar a versão `v1`). Faça o commit inicial conter
   *exatamente* os arquivos originais de `aljabr-v1` (sem nenhuma mudança).
   Somente depois disso, faça as mudanças especificadas para a linguagem nesta
   aula. Neste momento, seu foco devem ser os níveis léxico e sintático (que é
   o que vimos nesta aula). Mas vale a pena você tentar antecipar a
   implementação da semântica (da função `eval`). 
