# Derivação do pseudo-código BNF do parser de `calc`

## Sintaxe

```python
exp    ::= exp + termo | exp - termo | termo
termo  ::= termo * fator | termo / fator | fator
fator  ::= atomo ** fator | atomo
atomo  ::= INTEIRO | ( exp )
```

## Procedimento

Para cada regra A, vamos criar a função `parse_A()` cujo código espelha a
sequência de cada produção com `expect(T)` para cada terminal `T` ou com
`parse_B()` para cada não-terminal B que estiver na produção.

Sabemos que os ajustes que fizemos na gramática a tornam não ambígua. Contudo,
para decidirmos qual produção aplicar, preciamos usar _look-ahead_ (olhar
tokens adiante no stream) para decidir qual produção escolher. Idealmente,
queremos criar um parser LL(1), ou seja, que só olha um token à frente.

> Detalhe teórico aqui. O parser pode ser LL(1) se a gramática for LL(1). Em
> geral, gramáticas reais são LL(k) com esse k variando. Apesar disso, a
> maioria das linguagens simples e pequenas como a nossa acima são LL(1).


## Tentativa 1: derivação direta das regras

Comecemos da menor regra: `atomo`. Vamos criar `parse_atomo()`. A regra tem
duas produções: a primeira tendo apenas um terminal `INTEIRO` e a segunda sendo
a sequência de um terminal `(`, seguido pelo não-erminal `exp` e, por fim, mais
um terminal `(`. A decisão, portanto de qual aplicar pode ser feita apenas
olhando o primeiro token do stream: se é um `INTEIRO` ou um `(`.

```python
def parse_atomo():
   """atomo ::= INTEIRO | ( exp )"""

   if peek() == INTEIRO:       # look-ahead de 1 pra decidir a produção
      return expect(INTEIRO)   # era INTEIRO, aplica produção 1

   expect(`(`)           # o primeiro não era inteiro, deve ser LPAREN
   exp = parse_exp()     # recorre à função para exp
   expect(`)`)           # descarta o RPAREN pra concluir

   return exp       # retorna só o que interessa
```

A primeira regra foi fácil. Vamos pra segunda menor que é `fator`. Pra ela,
precisamos criar `parse_fator()`. Ela também tem apenas duas produções. A
primeira é a sequência do não-terminal `atomo`, do terminal `**`, seguido do
não terminal que estamos definindo `fator`. Essa produção será recursiva,
portanto. A segunda produção tem apenas um não-terminal: `atomo`.

Em princípio, você pode pensar que precisamos fazer um _look-ahead_ de dois
tokens para tomar uma decisão. Mas observe que as duas produções (que são todas
as existentes) são iniciadas pelo mesmo não terminal `atomo`. Isso nos permite
começar o código por `parse_atomo()`, para só então fazermos um _look-ahead_ de
um único elemento do stream e pra decidirmos qual caminho tomar depois disso. O
código abaixo faz exatamente isso.

```python
def parse_fator():
   """fator  ::= atomo ** fator | atomo"""

   atomo = parse_atomo()  # parte em comum pras duas produções

   if peek() != "**":  # look-ahead de 1
      return atomo     # não era `**`, aplica a segunda produção

   expect(`**`)                 # era um `**`, então descarta
   fator = parse_factor()       # chama a função recursivamente
   return [`**`, atomo, fator]  # retorna o nó da AST apropriado
```

Esta regra regra também foi fácil. Vamos para a terceira menor regra que é
justamente a relativa ao símbolo inicial de nossa linguagem: `exp`. Vamos
escrever `parse_exp()`.

Esta é uma regra com três produções. Comecemos escrevendo o pseudo-código de
cada uma das três produções em um bloco independente dos demais. A ideia é
separarmos a lógica interna de cada produção da lógica de decisão de qual delas
deve ser executada. Confira abaixo esses trechos, antes de abordarmos a lógica
de decisão.

```python
# produção 1: exp + termo
exp = parse_exp()
expect( + )
termo = parse_termo()
return ["+", exp, termo]

# produção 2: exp - termo
parse_exp()
expect( - )
parse_termo()
return ["-", exp, termo]

# produção 3: termo
parse_termo()
```

Os pseudo-códigos dos trechos relativos às regras já expõem um primeiro
problema. As duas primeiras produções obrigam a chamar recursivamente a própria
função que estamos querendo implementar que é `parse_exp()` sem que possamos
consumir nada do stream. Isso significa que isso já geraria uma recursão
infinita. 

Mesmo que conseguíssemos driblar de alguma forma a recursão infinita, ainda há
outro problema (relacionado, na verdade). É que não temos como decidir qual das
três produções aplicar olhando apenas um token à frente no stream. Observ que
`PRIMEIRO(exp)` é igual a `PRIMEIRO(termo)` e isso torna impossível decidir
qual produção aplicar.

Além disso, é fácil ver que os terminais `+` e `-` que diferenciam as duas
primeiras produções só vão aparecer no stream depois que um `termo` tiver sido
processado (reflita sobre isso usando a própria regra de `exp`). Ou seja, a
decisão não é possível no começo da regra, só é possível decidir qual regra
aplicar depois do primeiro procerssamento completo de `parse_termo()`. Mais que
isso, como o número de tokens necessários até termos concluído um `termo`
completo é ilimitado, não há qualquer valor k que permita usar um _look-ahead_
LL(k) com k > 1 que possa funcionar.

> Vou aproveitar aqui o gancho dessa observação. A única possibilidade seria
> poder ir à frente com o processo de análise e no stream até acharmos o `+` ou
> o `-` e só então voltar para aplicarmos a regra. Essa, contudo, é uma
> estratégia de parsing completamente diferente da usada por analisadores
> descendentes recursivos. Nessas abordagens, há analisadores _bottom-up_,
> parsers LR, parsers que usam _backtracking_, etc. No curso, estamos apenas
> vendo a abordagem descendente recursiva, em particular a LL (_Left-to-right,
> Leftmost derivation)..


## Tentativa 2: derivação direta das regras

> IMPORTANTE: Esta parte do texto pressupõe que o aluno tenha visto a conteúdo
> sobre transformações de gramáticas.

Na tentativa 1, acima, vimos que a gramática apresentada não é apropriada para
a derivação direta das funções de um parser LL(1). Isso ocorre por dois
motivos: primeiro, porque a gramática inclui regras com recursão à esquerda; e,
segundo, porque para as regras escritas não é possível o uso de _look-ahead_ de
um token para a escolha das regras (para qualquer valor de k).

Dito isso, agora que vimos que gramáticas podem ser tranformadas em outras
equivalentes (que expressam a mesma linguagem), através de transformações que
podem ser aplicadas mecanicamente.

### Refatorando a gramática de `calc` 

Na gramática vista, há duas regras que requerem ajuste. Por quê? Porque ambas
usam recursão à esquerda. Abaixo as duas regras.

```
exp    ::= exp + termo | exp - termo | termo
termo  ::= termo * fator | termo / fator | fator
```

#### Passo 1: vamos eliminar a recursão à esquerda

Esta é a regra que precisaremos:

```
A ::= A α1 | A α2 | β
==>
A ::= β A'
A' ::= α1 A' | α2 A' | ε
```

Primeiro, façamos para `exp`

```python
exp   ::= termo exp'
exp'  ::= + termo exp' | - termo exp' | ε
```
Em seguida, façamos para `termo`

```python
termo   ::= fator termo'
termo'  ::= * fator termo' | / fator termo' | ε
```

#### Passo 2: Fatoramento à esquerda de `fator`

A regra `fator` tem um prefixo comum: `atomo`. Então, podemos colocá-lo em
evidência:

```python
fator   ::= atomo fator'
fator'  ::= ** fator | ε
```

#### Passo 3: Introdução agrupamento (aqui passamos para EBNF)

Esta é a gramática após as transformações acima. Observe que eliminamos a
recursão à esquerda, mas tivemos que introduzir três não-terminais: `exp'`,
`termo'` e `fator'`.

```python
exp     ::= termo exp'
exp'    ::= + termo exp' | - termo exp' | ε

termo   ::= fator termo'
termo'  ::= * fator termo' | / fator termo' | ε

fator   ::= atomo fator'
fator'  ::= ** fator | ε

atomo   ::= INTEIRO | ( exp )
```

Para simplificar a gramática acima, usemos o agrupamento EBNF para reduzir as
produções de `exp'` (veja que isto equivale a um fatoramento à direita
simétrico ao que vimos à esquerda). Assim, em vez de `+ termo exp'` e `- termo
exp'` podemos ter ou um `+` ou um `-` seguido de `termo exp'`. Isso em EBNF
pode ser expresso usando o agrupamento e o operador de alternativa `|`. Abaixo,
a gramática após fazer essas transformações em `exp'` e também o equivalente em
`termo'`.

```python
exp     ::= termo exp'
exp'    ::= ( + | - ) termo exp' | ε

termo   ::= fator termo'
termo'  ::= ( * | / ) fator termo' | ε

fator   ::= atomo fator'
fator'  ::= ** fator | ε

atomo   ::= INTEIRO | ( exp )
```

#### Passo 4: eliminação das produções vazias

Após a simplificação acima, observe que o propósito sintático de `exp'`,
`termo'` passou a ser o mesmo de `fator'` que é o de tornar opcional a
continuação da expressão opcional (daí que todos têm uma produção simples e
outra vazia). Logo, podemos voltar a unificar essas regras às de base
correspondentes, usando o operador opcional de EBNF para eliminar o `ε`.

```python
exp     ::= termo { ( '+' | '-' ) termo }
termo   ::= fator { ( '*' | '/' ) fator }
fator   ::= atomo [ '**' fator ]
atomo   ::= INTEIRO | '(' exp ')'
```

E esta é a gramática de `calc` totalmente adaptada para nossa implementação do
parser descendente recursivo LL(1).

### Nova codificação da associatividade

Um aspecto importante a observar na gramática resultante é o que ocorreu com a
propriedade da associatividade. 

No momento inicial, em que projetamos a gramática, introduzimos a
associatividade deliberadamente à esquerda, porque é o tipo de associatividade
desejada para a linguagem que melhor se adapta à operação (semântica). O
processo de transformação, contudo, eliminou a recursão à esquerda e, portanto,
também eliminou a garantia de associatividade à esquerda.

Quando usamos `{ … }` como forma de dar continuidade a `exp` ou a `termo` em
vez do mecanismo original que era recursão à esquerda, passamos a uma recursão
à direita, mas cuja leitura convencional é, tipicamente, que se trata de uma
forma _flat_, n-ária que não determina como deve ser a associatividade! É como
se estivéssemos de volta a s-expressões. A interpretação convencional de
repetições em EBNF é que um `exp` é um `termo` seguido por qualquer quantidade
de sequências com um operador e outro `termo`. 

Com isso, expressões com sintaxe concreta igual a `2 + 3 + 4` podem ser vistas
como tendo sintaxe abstrata igual a `Soma(2, 3, 4)`. Da mesma forma, subtrações
cuja sintaxe concreta é `2 - 3 - 4` terá sintaxe abstrata `Subtração(2, 3, 4)`.
Com isso, se delega a uma _ação semântica_ a decisão de como efetivamente
produzir a AST. Esse processo é denominado de _folding_ e deve ser
implementado no interpretador.

 
### Hora de produzir pseudo-código para o parser

```python
exp     ::= termo { ( + | - ) termo }
termo   ::= fator { ( * | / ) fator }
fator   ::= atomo [ ** fator ]
atomo   ::= INTEIRO | ( exp )
```

O pseudo-código de `parse_atomo()` permanece o mesmo.

```python
def parse_atomo():
   """atomo ::= INTEIRO | ( exp )"""

   if peek() == INTEIRO:       # look-ahead de 1 pra decidir a produção
      return expect(INTEIRO)   # era INTEIRO, aplica produção 1

   expect(`(`)           # o primeiro não era inteiro, deve ser LPAREN
   exp = parse_exp()     # recorre à função para exp
   expect(`)`)           # descarta o RPAREN pra concluir

   return exp       # retorna só o que interessa
```

Agora, vejamos como fica `parse_fator()`.

```python
def parse_fator():
   """fator  ::= atomo [ ** fator ]"""

   atomo = parse_atomo()  # parte em comum pras duas produções

   if peek() != "**":  # look-ahead de 1
      return atomo

   expect("**")                 # era um `**`, então descarta
   fator = parse_fator()        # chama a função recursivamente
   return ["**", atomo, fator]  # monta o nó da AST
```

Passemos agora, à implementação de `parse_termo()`. 

```python
def parse_termo():
   """termo ::= fator { ( * | / ) fator }"""
   fator = parse_fator()
   while peek() in ['*', '/']:
      op = expect(TOKEN)           # lê o operador
      fator2 = parse_fator()       # lê um fator
      fator = [op, fator, fator2]  # faz o folding à esquerda

   return fator
```

Finalmente, passemos à implementação de `parse_exp()`.

```python
def parse_exp():
   """exp ::= termo { ( + | - ) termo }"""
   termo = parse_termo()
   while peek() in ['+', '-']:
      op = expect(TOKEN)           # lê o operador
      termo2 = parse_termo()       # lê um novo termo
      termo = [op, termo, termo2]  # faz folding à esquerda

   return termo
```
