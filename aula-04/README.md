# Aula 04 — 21/Set — Estágio 2 (Semana 2)

> m2lisp: 
> - adicionando suporte para operações com múltiplas aridades 
> - adicionando input `?`


## Revisão e pequena atualização

- rpn praticamente dispensa parser, porque sua sintaxe foi intencionalmente
  projetada para facilitar a interpretação via uma pilha

- mlisp também foi projetada para ter sintaxe concreta estruturalmente igual
  à sintaxe abstrata (código lisp reflete a estrutura da AST correspondente);
  isso nos permitiu implementar um parser de forma intuitiva, baseado no
  algoritmo de pareamento de parênteses;

- para esquentar os motores, vamos evoluir o interpretador mlisp para suportar
  operações com aridades distintas, incluindo operações variádicas; a ideia é
  aproximar ainda mais nossa linguagem do Lisp clássico, em que a sintaxe
  apenas determina que s-expressões são iniciadas por um operador e, em
  seguida, têm um número livre de argumentos;

- a variação está no arquivo `mlisp-v2.py`


## Abordagem do novo conteúdo da aula

- Apresentar especificações formais de léxico e sintático de mlisp

- Reimplementar lexer e parser mlisp a partir das especificações formais

- Apresentar EBNF como alternativa

- Reimplementar lexer e parser a partir de EBNF

- Concluir com breve menção ao léxico e sintaxe da notação infixa
  - e apontar um novo problema: precedência de operadores


## Formalização do léxico e da sintaxe de mlisp com REGEX, BNF

Depois de evoluirmos mlisp, passamos à especificação formal do léxico e da
sintaxe da linguagem.

### Léxico de mlisp

Para `mlisp` o nível **léxico** prevê apenas quatro tipos de tokens. Abaixo
especifico cada um deles, através das seguintes expressões regulares.;

```
LPAREN    ::=  (
RPAREN    ::=  )
OPERADOR  ::=  [+-*/]
INTEIRO   ::=  [0-9]+
```

É importante reforçar a terminologia que usamos. Cada tipo de token (INTEIRO,
OPERADOR, …) é formalmente chamado de _categoria léxica_. A especificação de
cada tipo de token é dada através das linhas acima que têm o tipo do token à
esquerda, o símbolo `::=` e a especificação em formato de expressão regular à
direita. Esses mesmos tipos de tokens ou categorias léxicas são chamados de
_terminais_ quando os mencionamos no contexto de análise sintática. 


### Sintaxe de mlisp

A sintaxe de mlisp é bem simples também. Relembre que é baseada em s-expressões
que, por sua vez, são _expressões prefixas parentizadas_. Isso nos permite usar
uma gramática em estilo BNF extremamente simples, com apenas 3 regras (obverve
que aqui usamos as categorias léxicas que definimos no léxico acima).

```
<s-expressão>  ::=  LPAREN OPERADOR <argumentos> RPAREN
<argumentos>   ::=  <arg> <argumentos> | ε
<arg>          ::=  INTEGER | <s-expressão>
```

> O símbolo `ε` denota uma derivação vazia.

Especificações sintáticas como essas acima são chamadas de _gramáticas_. A
notação específica usada é a BNF (Backus Naur Form). Gramáticas BNF consistem
em um conjunto de _regras de produção_ na forma

`<não-terminal> ::= <produção-1> | <produção-2> …`

As regras definem as chamadas _categorias sintáticas_ (`<s-expressão>`,
`<argumentos>` e `<arg>`, na gramática acima) que também são chamadas de
_não-terminais_. As produções também podem mencionar tipos de tokens (`LPAREN`,
`OPERADOR`, `INTEGER` e `RPAREN` em nosso exemplo); os tipos de tokens mencionados nas regras de produção também são chamados de _terminais_.

Os termos _terminais_ e _não-terminais_ fazem referência aos processos de
derivação, usando as regras de produção. Um programa concreto é produzido a
partir de uma derivação quando não houver mais nenhum _não-terminal_ que possa
ser derivado. Nesse momento, a expressão terá apenas tokens ou _terminais_ da
linguagem.

### Exemplo de derivação

Abaixo, mostro um exemplo de derivação possível do terminal que define os
programas em nossa linguagem: `<s-expressão>`.

```
<s-expressão>
⇒ LPAREN OPERADOR <argumentos> RPAREN
⇒ ( OPERADOR <argumentos> )
⇒ ( + <argumentos> )
⇒ ( + <arg> <argumentos> )
⇒ ( + INTEGER <argumentos> )
⇒ ( + 2 <argumentos> )
⇒ ( + 2 <arg> <argumentos> )
⇒ ( + 2 <s-expressão> <argumentos> )
⇒ ( + 2 LPAREN OPERADOR <argumentos> RPAREN <argumentos> )
⇒ ( + 2 ( OPERADOR <argumentos> RPAREN <argumentos> )
⇒ ( + 2 ( * <argumentos> ) <argumentos> )
⇒ ( + 2 ( * <arg> <argumentos> ) <argumentos> )
⇒ ( + 2 ( * INTEGER <argumentos> ) <argumentos> )
⇒ ( + 2 ( * 3 <argumentos> ) <argumentos> )
⇒ ( + 2 ( * 3 <arg> <argumentos> ) <argumentos> )
⇒ ( + 2 ( * 3 INTEGER <argumentos> ) <argumentos> )
⇒ ( + 2 ( * 3 4 <argumentos> ) <argumentos> )
⇒ ( + 2 ( * 3 4 ) <argumentos> )
⇒ ( + 2 ( * 3 4 ) )
```

A ideia com o uso de gramáticas é que elas especificam precisamente o conjunto
de todos os programas possíveis de escrever na LP. Ou seja, se há alguma
derivação possível para um certo texto, então esse texto é um programa válido
na linguagem. E o contrário também vale: para todo programa válido da
linguagem, há uma derivação possível a partir do não-terminal que define os
programas. Qualquer texto para o qual não haja derivação completa é um programa
sintaticamente incorreto.


## Especificação formal como base para a implementação

Além de servir como forma abstrata e precisa de especificação do léxico e da
sintaxe de uma linguagem, as especificações formais vistas também são usadas
como base para a implementação do lexer e do parser da linguagem. 

Relembre as implementações do lexer e do parser que fizemos para RPN e para
nossa versão inicial de mlisp. Ambas foram baseadas em uma intuição sobre o
léxico e a sintaxe das linguagens. Isso, contudo, só é possível porque as
linguagens são muito simples (de fato, elas foram projetadas para garantir essa
simplicidade).

Qualquer LP real, contudo, tem regas léxicas e sintáticas significativamente
mais complexas do que RPN e mlisp. E, por isso, construir um parser para LPs
reais requer uma estratégia melhor que não dependa de intuição. E nesse
propósito que especificações formais de léxico e de sintaxe se mostram
especialmente interessantes.

De modo geral, podemos dizer que se temos as especificações formais do léxico e
da sintaxe de uma LP nas formas acima descritas, será relativamente fácil
produzir os algoritmos do lexer e do parser da linguagem.


### Parser descendente recursivo

**Lexer** Para produzir o lexer, vimos que o uso de expressões regulares é
praticamente direto. Aqui, por simplicidade, vou assumir que para cada
definição de tipo de token teremos uma função booleana que verifica se um token
pertence ou não àquela categoria léxica. Para nossa LP, podemos definir as
funções como abaixo (observe que usei lambdas para esse propósito, apenas por
simplicidade do código).

```
import re

LPAREN = lambda tok: tok == "("
RPAREN = lambda tok: tok == ")"
OPERADOR = lambda tok: re.fullmatch(r"[+-*/]", tok) is not None
INTEIRO = lambda tok: re.fullmatch(r"[0-9]+", tok) is not None
```

**Parser** Para o analisador sintático, o processo é semelhante: cada
não-terminal da gramática será uma função do parser que verifica a regra de
produção do não-terminal e que retorna ou um nó da AST ou um erro.
Naturalmente, a função só retorna um nó da AST se for verificada a conformidade
da sequência de tokens à regra. Veja, por exemplo, a regra abaixo.

```
<s-expressão>  ::=  LPAREN OPERADOR <argumentos> RPAREN
```

Essa regra especifica o não-terminal `s-expressão`. Teremos, portanto, a função
`parse_s_expressao(stream) -> Ast | Erro`. Observe que a produção especificada
pela regra (parte do lado direito do `::=`) pode ser vista como a especificação
do que a função deve verificar na sequência de tokens a ser obtida do `stream`.
A especificação diz explicitamente que devem ser observados um `LPAREN`,
seguido de um `OPERADOR`, seguido de `<argumentos>` e, por fim, concluído por
um `RPAREN`. Se o `stream` de tokens contiver esses elementos, a s-expressão
terá sido reconhecida com sucesso. O código abaixo expressa esse comportamento
(em pseudo-código). Lembre que em nossa implementação, uma `Ast` é uma lista
contendo um operador na primeira posição e os argumentos nas demais (sendo que
os argumentos podem ser eles próprios outras `Ast`s; afinal, é uma árvore).

```Python
def parse_s_expressao(stream) -> Ast | Erro:
    """<s-expressão>  ::=  LPAREN OPERADOR <argumentos> RPAREN"""

    # abaixo vemos os quatro elementos da produção especificada
    # cada passo pode dar errado… nesse caso, deve retornar um Erro
    expect(LPAREN)
    op = expect(OPERADOR)
    args = parse_argumentos(stream)
    expect(RPAREN)

    # se chegamos aqui, é pq tudo deu certo: retorna a Ast
    return [op, *args]
```

O código acima é obtido de forma quase que mecânica a partir da gramática BNF.
Para isso, use a correspondência abaixo para cada parte da gramática.

| Na BNF            | Parser descendente recursivo                                        |
|-------------------|---------------------------------------------------------------------|
| não-terminal <A>	| parse_a()                                                           |
| A ::= B C	        | chama parse_b() e depois parse_c()                                  |
| A ::= B | C	      | decide entre parse_b() e parse_c() com base no próximo terminal (*) |
| A ::= ε	          | retorna sem consumir token                                          |
| A ::= B A	        | recursão                                                            |
| terminal TOKEN	  | expect(TOKEN)                                                       |


(*) IMPORTANTE: nesta conversão, precisamos olhar um token do stream, sem
consumi-lo. Perceba que a ideia é apenas ver qual será o próximo token pra
decidirmos qual das duas opções de produção deve ser escolhida (ou `B` ou `C`
quando a forma é `B | C`). Quando a gramática exige que olhemos apenas um token à frente, dizemos que ela é LL(1).

> LL significa _Left-to-right Left-most_ em referência à forma como a escolha
> da derivação é feita.

### peek: olhando o próximo token

Sempre que for necessário olhar o conteúdo do stream, sem consumi-lo, usaremos
a operação a que chamaremos de `peek` (às vezes também chamada de
`next_token`). Veja o exemplo de função abaixo que foi feita para a regra que
define o não terminal `<arg>`. Perceba que o pseudo-código primeiro verifica se
o próximo token do stream é `INTEGER`. Se for, a primeira produção é usada. Só
então, um token é efetivamente consumido do stream e é retornado. Relembre que
um inteiro é uma Ast válida, já que é uma folha da árvore.

Por outro lado, se o primeiro token do stream não for um inteiro, é preciso
concluir que a primeira produção da regra não poderá ser usada e, portanto, é
preciso considerar a segunda alternativa. É por isso que o token não pode ser
consumido de imediato. O stream, nesse caso, permanecerá inalterado e poderemos
passar à segunda produção. Como a segunda produção é iniciada por uma
`<s-expressão>` e como sabemos que toda s-expressão é iniciada por um `LPAREN`
podemos usar isso para determinar se podemos mesmo aplicar a produção. É isso
que o segundo `if` abaixo faz. Mais uma vez, o token é apenas lido, mas não
consumido, de forma que possamos invocar a função `parse_s_expressao(stream)`
com o token ainda no stream.

```python
def parse_arg(stream) --> Ast | Erro:
    """<arg>  ::=  INTEGER | <s-expressão>"""

    # primeiro sondamos o stream para a primeira produção
    # é um inteiro o primeiro token do stream?
    if peek(INTEGER):
        return expect(INTEGER)

    # o primeiro token não é um inteiro, vamos à segunda produção
    # para isso, é necessário que seja um LPAREN (início de uma s-expressão)
    if peek(LPAREN):
        return parse_s_expressao(stream)

    return Erro("esperado inteiro ou s-expressão")
```

Abaixo o pseudo-código completo do parser que podemos obter diretamente de
nossa gramática. Desta vez, sem os comentários explicativos que adicionei
acima.

```Python
def parse_s_expressao(stream):
    """<s-expressão>  ::=  LPAREN OPERADOR <argumentos> RPAREN"""
    expect(LPAREN)
    op = expect(OPERADOR)
    args = parse_argumentos(stream)
    expect(RPAREN)
    return [op, args]

def parse_argumentos(stream):
    """<argumentos>   ::=  <arg> <argumentos> | ε"""
    if peek(RPAREN):
        return []
    arg = parse_arg(stream)
    argumentos = parse_argumentos(stream)
    return [arg] + argumentos

def parse_arg(stream):
    """<arg>          ::=  INTEGER | <s-expressão>"""
    if peek(INTEGER):
        return expect(INTEGER)
    if peek(LPAREN):
        return parse_s_expressao(stream)
    return Erro("esperado inteiro ou s-expressão")
```


### Concretizando o parser

O pseudo-código acima é apropriado para dar uma compreensão global das partes
do parser produzido por esta abordagem, mas ainda não é o código real. Para isso, é necessário ajustar vários detalhes. O mais importante é entender como as pseudo-funções (ou macros) `expect()` e `peek()` devem ser efetivamente implementadas.

Comecemos com `expect(TOKEN)`. Observe que ela especifica que é necessário
consumir um token do stream e confrontá-lo com a categoria léxica indicada. Se
o token corresponder, ele pode ser ou ser descartado ou guardado, caso haja uma
atribuição explícita. Vamos assumir que o `stream` é um objeto com o método
`next()` que permite consumir um token. Esse método, portanto, deve retornar ou
um token ou `None` para indicar que o stream foi todo consumido. O código
abaixo, portanto, permite ver como o que especificamos acima simplesmente como
`expect(TOKEN)` deve ser de fato implementado.

```Python
def parse_s_expressao(stream: Iterador[str]) -> Ast | Erro:
    """<s-expressão>  ::=  LPAREN OPERADOR <argumentos> RPAREN"""

    # expect(stream, LPAREN)
    if not LPAREN(stream.next()):
        return Erro("expected LPAREN, not found")

    # op = expect(OPERADOR)
    if not OPERADOR(op := stream.next()):
        return Erro("expected OPERADOR, not found")

    erro = args = parse_argumentos(stream)
    if isinstance(erro, Erro):
        return erro

    # expect(RPAREN)
    if not RPAREN(stream.next())
        return Erro("expected RPAREN, not found")

    # como tudo deu certo, retorna o nó da AST
    return [op, args]
```

> Nesse código acima faço uso de duas facilidades de Python que você talvez não
> conheça, mas que vale a pena dar uma estudada: o operador de atribuição `:=`
> conhecido por operador _walrus_; e a chamada atribuição encadeada (ou por
> encadeamento): `a = b = <expressão>`. Ambas facilitam e simplificam um pouco
> o código acima. Não acredita? Reescreva o código acima sem elas e veja como
> ficaria.

Abaixo, sigo com a implementação detalhada do pseudo-código que usa a
pseudo-função `peek()`. Relembre que ela é usada sempre para ler um token do
stream e verificar se é do tipo correto, sem efetivamente consumi-lo do stream.
Para isso, vamos assumir que o stream é implementado suportando o chamado
_look-ahead_ de um elemento. Isso é suficiente para nosso parser, porque, como
disse anteriormente, nossa gramática é LL(1)… ou seja, para decidirmos qual
produção usar, precisamos olhar apenas um token à frente no stream.

```Python
def parse_argumentos(stream):
    """<argumentos>   ::=  <arg> <argumentos> | ε"""
    # if peek(RPAREN): return []
    if RPAREN(stream.peek()):
        return []

    # arg = parse_arg(stream)
    erro = arg = parse_arg(stream)
    if isinstance(erro, Erro):
        return erro

    # argumentos = parse_argumentos(stream)
    erro = argumentos = parse_arg(stream)
    if isinstance(erro, Erro):
        return erro

    return [arg] + argumentos
```
