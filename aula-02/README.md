# Aula 02

## Parte 1: revisão do conteúdo visto

> Qual a questão central abordada? O que ocorre com um programa
> desde o momento que concluímos sua escrita até o momento em que
> produz um resultado?


### O pipeline de processamento

Na aula passada, vimos que o processamento de uma LP se dá
através de um _pipeline_, uma sequência de operações em que cada
operação consome o dado produzido pela etapa anterior e produz um
novo dado para a etapa posterior. Este é o pipeline que definimos
para o processamento de nossa LP objeto (RPN):

  código fonte
       ↓
   [ lexer ]
       ↓
    tokens
       ↓
  [ parser ]
       ↓
programa validado
       ↓
[ interpretador ]
       ↓
   resultado

> No esquema acima estão intercalados os dados (código fonte,
> tokens, programa validado, resultad) e as operações (lexer,
> parser e interpretador) do pipeline.

### Refatoramento: as constantes OPERADORES e OPERACAO

Como iniciamos a aula com o código que deixamos na aula anterior
(arquivo `rpn.py` da aula anterior), em que só tínhamos uma única
operação de nossa linguagem objeto (operação soma, operador `+`),
iniciamos adicionando uma nova operação à LP: a operação
subtração (com o operador `-`). A adição dessa operação foi
extremamente simples, já que consistiu em revisar cada estágio do
pipeline e introduzir o devido tratamento.

O mais importante dessa ação é que nos permitiu perceber uma
oportunidade de generalizar o processo. Foi o que nos levou a
definir explicitamente as constantes `OPERADORES` e `OPERACAO`
em nosso interpretador. A primeira constante é usada para
expressar o conjunto de `OPERADORES` de nossa linguagem. Serve,
portanto, como suporte para a descrição do léxico de nossa LP. Já
o dicionário `OPERACAO` é usado para mapear os operadores às
respectivas operações (binárias), servindo de apoio à
especificação semântica da LP (exatamente porque conecta os
operadores da LP às operações a serem executadas).

> Uma vez concluído o refatoramento do código para usar as duas
> constantes acima mencionadas, ficou facilitada a adição dos
> outros dois operadores com facilidade.

### Tratamento de Erros

Nosso interpretador (até este ponto da aula, ver arquivo `rpn.py`
desta aula) não lida bem com erros nos programas que podem ser
processados. De fato, um erro de programação faz nosso
interpretador _quebrar_ em tempo de execução.

> Teste o interpretador `rpn.py` (desta aula) com entradas com
> variados erros: 1) léxicos; 2) sintáticos e 3) semânticos (de
> tempo de execução). Observe que o interpretador quebra a
> execução porque nossa lógica usa `raise` sempre que alguma
> situação é detectada.

Um tratamento mais apropriado (que usarei no curso) para erros em
pipelines é usar o que se conhece por _tratamento monádico de
erro_ (não se preocupe com o nome, você vai ver que a ideia é
simples, embora num primeiro momento possa parecer estranha e um
pouco enrolada). 

A ideia central é tornar os erros em possíveis significados dos
programas (dos programas errados, naturalmente). Pense no tipo
`Erro` como uma variação do tipo de dado `Exception` que você já
conhece de Python e Java. Por simplicidade, definiremos nossos
erros como simples strings (veja o arquivo `erros.py` em que
definimos Erro como um alias de str).

> Como comentamos em sala de aula, esta implementação tem uma
> limitação: só faz sentido usá-la porque as funções do pipeline
> em que precisaremos usá-las nem recebem strings, nem retornam
> strings. Se precisarmos, mais adiante, podemos melhorar a
> implementação do tipo Erro, usando uma classe, por exemplo.

Além do tipo `Erro`, também introduzi o _decorator_
`monadic_error`. Trata-se de uma função que apenas atua como
intermediária na invocação de outra função. Quando decoramos as
funções `parser` e `interpretador` com `@monadic_error`, estamos
adicionando um intermediário na invocação da função. Em vez da
função decorada ser chamada diretamente, ela passa a ter um
pré-tratamento em que se verifica se o tipo de dado recebido é um
`Erro`. Se for, esse erro é retornado sem invocar efetivamente a
função decorada. Já se o dado não é um `Erro`, a função decorada
é invocada com os exatos mesmos argumentos recebidos pela função
intermediadora (veja a função `wrapper` dentro de `erros.py`,
caso queira entender isso melhor).

O efeito desse "malabarismo" é que o pipeline formado pelas
funções `tokenizador`, `parser` e `interpretador` agora podem
lidar facilmente com erros. Em vez de cada possível erro nos
obrigar a usar cláusulas `try..except` aninhadas, podemos
simplesmente escrever o código `main` como o escrevemos e saber
que o erro simplesmente vai fluir desde o ponto onde ocorreu até
o fim do pipeline, para que seja devidamente impresso pela linha
final da função `main`.

Mas é importante destacar. Usei o padrão monádico de tratamento
de erro por um motivo maior que o de simplesmente eu preferir
esse estilo de tratamento de erro ao convencional `try..except`:
é que ao expressarmos o interpretador dessa forma, vemos
claramente que Erros são possíveis significados de programas (ou
candidatos a programas) que o usuário de uma linguagem de
programação possa produzir. E nosso interpretador agora calcula e
imprime esse significado explicitamente para qualquer programa
(com erro).

> Desta vez, teste o interpretador `rpn2.py` com entradas com as
> mesmas entradas com erros que você experimentou anteriormente.
> Tente erros: 1) léxicos; 2) sintáticos e 3) semânticos.
> Observe que nosso novo interpretador NÃO quebra e que a
> execução, corretamente, imprime o significado dos programas
> errados, indicando isso explicitamente.

## Parte 2: Meta-linguagens formais de especificação

> Questão central: como podemos expressar regras léxicas,
> sintáticas e semânticas de uma LP que desejamos projetar?

Linguagens usadas para expressar propriedades de outras
linguagens são ditas **meta-linguagens**. Então, a pergunta acima
poderia ser expressa assim: que linguagens podemos usar como
meta-linguagens para o propósito de expressarmos e projetamos as
características de uma LP? Há diferenças entre essas
meta-linguagens? Como escolhemos quais podemos/devemos usar?

### Linguagem natural + implementação de referência

Até este ponto do curso, usamos duas linguagens como
meta-linguagens: linguagem natural (português em nosso caso) e
uma linguagem de programação (Python). De fato, poderíamos até
termos focado em apenas uma delas e não ter usado a outra, mas
isso teria claras consequências.

Usando apenas linguagem natural teríamos dificuldades com
ambiguidades, prolixidade, clareza, além de dificuldades de para
expressar raciocínios sobre as propriedades da linguagem e seus
elementos, etc (além disso, não teríamos uma versão utilizável da
LP). Usando apenas apenas Python também teríamos dificuldades: se
considerarmos que o código do interpretador é a especificação da
LP, então compreender Python se torna quase que obrigatório para
compreender a linguagem. Além disso, se a implementação contiver
erros, será difícil separá-los da especificação correta. E, por
fim, expressar raciocínios sobre propriedades da da LP também não
será mais fácil.

É por isso que optei por usar um mix das duas linguagens para
especificar RPN pra vocês: um pouco de português e um
interpretador em Python. De fato, na prática, essa combinação é
muito usada: documentos em linguagem natural, combinados com uma
implementação de referência. 

### Meta-linguagens formais para léxico e sintático

Uma forma de encararmos o interpretador que construímos é como _a
especificação_ da linguagem RPN. Nesse caso, pela falta de um
documento formal, o interpretador passa a ser a referência
oficial (_a fonte da verdade_) da LP. 

Uma outra forma de encararmos o interpretador é como _uma
implementação_ da linguagem RPN (veja isso em oposição a ele ser
_a especificação_). Essa pequena diferença nos permite
questionar: e qual é a especificação? Se quisermos implementar
RPN em outra linguagem de programação, qual especificação podemos
usar como referência? É para esse propósito que nos leva a adotar
meta-linguagens mais matemáticas e abstratas para especificar
LPs. 

**Conjuntos e Expressões Regulares** O léxico de uma linguagem
(uma LP) é simplesmente o conjunto de todos os possíveis _tokens_
que se pode usar na LP. Para especificar tais tokens, usaremos
teoria dos conjuntos e expressões regulares (união, concatenação
e iteração). Para caracterizarmos o léxico de RPN, precisamos de
um alfabeto pequeno de caracteres: 

> Alfabeto de RPN: `0`, `1`, …, `9`, `+`, `*`, `-`, `/`  e ` ` 

Observe que todos os _tokens_ de nossa LP são combinações dos
caracteres acima: `12`, `10`, `471`, `+`, etc. Apesar disso, nem
todas as combinações são tokens válidos: `++`, `*1*`, etc. Por
isso, precisamos de uma especificação precisa e, para isso,
usamos expressões regulares:

```
DÍGITO   ::=  '0' | '1' | … | '8' | '9'
OPERADOR ::=  '+' | '-' | '*' | '/'
NÚMERO   ::=  DÍGITO DÍGITO*
TOKEN    ::=  NÚMERO | OPERADOR
```

> As expressões acima definem quatro tipos de tokens: DíGITO
> (qualquer um dos caracteres indicados), OPERADOR (semelhante),
> NÚMERO (definido como um DÍGITO concatenado a um DÍGITO que
> pode ser reptido 0 ou mais vezes) e TOKEN (definido como sendo
> ou um NÚMERO ou um OPERADOR). 

O tipo de token mais interessante aqui é NÚMERO. Observe que a
especificação é fácil de entender. Ela diz que um número deve ter
no mínimo um, mas que pode ter uma quantidade ilimitada de
DÍGITOs. Essa formação usa duas operações de expressões
regulares: concatenação e iteração (é a concatenação de um dígito
com um dígito que pode iterado qualquer número de vezes). Observe
que não seria possível definir `NÚMERO ::= DÍGITO*` porque a
iteração, representada por `*`, expressa um número qualquer de
repetições do elemento, incluindo zero repetições. É o uso de
`DÍGITO DÍGITO*` que garante que um número precisa começar com um
DÍGITO.

```
NÚMERO    ::=  [0-9]+
OPERADOR  ::=  [+-*\] 
ESPAÇO    ::=  \s+
```

> Chamar a atenção para a simplicidade da especificação léxica acima. É
> compacta, legível e implementável de forma quase trivial na maioria das LPs
> (além de ser de processamento eficiente).


**Gramáticas BNF** Para expressar as regras sintáticas de
nossa LP usaremos gramáticas. Mais precisamente usaremos a
meta-linguagem conhecida por BNF (_Backus Naur Form_). Abaixo,
expresso um exemplo simples de regra BNF que expressa toda a
sintaxe da linguagem RPN.

```
<expr-rpn> ::= NÚMERO | <expr-rpn> <expr-rpn> OPERADOR
```

A regra acima especifica o que é uma `expr-rpn` (um program RPN
ou simplesmente uma _expressão RPN_). Veja que a especificação é
_recursiva_, já que a própria categoria `expr-rpn` que está sendo
definida é usada em uma das regras de derivação. Vejamos cada uma
das regras separadamente.

```
<expr-rpn> ::= NÚMERO
```

Esta primeira regra diz que um programa RPN pode ser simplesmente
um NÚMERO. De fato, programas como `100` ou `123` são
perfeitamente válidos (seus significados são exatamente os
valores desses números). Vejamos a segunda derivação possível.

```
<expr-rpn> ::= <expr-rpn> <expr-rpn> OPERADOR
```

Esta derivação diz que dados dois programas RPN válidos, digamos
`A` e `B` é perfeitamente possível combiná-los em um programa
maior simplesmente compondo-os na ordem: `A B op` onde `op` é um
dos OPERADORES da linguagem. Por exemplo, se `A` é `1 2 +` e `B`
é `100`, então `1 2 + 100 *` é também um programa sintaticamente
válido. A regra estabelece duas coisas: 1) que qualquer programa
que possamos derivar dessa forma é considerado (sintaticamente)
válido; e 2) que todo e qualquer programa RPN válido deve poder
ser derivado dessa regra (ou seja, não há programas RPN válido
que não se possa derivar dela).

> Observe como a especificação acima é apropriada para expressar
> sintaxe. Ela deixar evidente a ordem exigida dos elementos.
> Além disso, se articula perfeitamente com a especificação
> léxica, já que permite referenciar os tipos léxicos nas regras.


**Regras de transição e semântica** Por fim, para expressarmos
formalmente a semântica de LPs, usarmos o que chamamos de _regras
de transição_ (mais adiante veremos outras formas de expressar
semântica). A ideia é caracterizar a semântica como a sequência
de passos necessários para o processamento do programa,
especificando regras que dizem como passar de um estado para
outro, à medida que cada token do programa é processado. Cada
regra de transição expressa o estado de partida a que se aplica a
regra e o estado de chegada. A avaliação consiste em detectar
qual regra se pode aplicar a cada instante até que nenhuma regra
mais possa ser aplicada.

As regras de transição para RPN podem ser expressas com um estado
definido em duas partes: o par `⟨tokens-a-processar, pilha⟩`.
Como só temos dois tipos de tokens a considerar, precisamos
apenas de duas regras para RPN:

```
⟨N · restante, pilha⟩
        → 
⟨restante, N :: pilha⟩
```

> Nessa regra, o meta-operador `·` expressa que a expressão
> inicial inicial é composta por `N` seguido do `restante` da
> entrada ainda a ser processada. Da mesma forma o meta-operador
> `::` expressa que a pilha após o processamento é idêntica à
> primeira, mas com o valor `N` adicionado a seu topo.

A segunda regra é dada abaixo.

```
⟨+ · restante, a :: b :: pilha⟩
        →
⟨restante, (b + a) :: pilha⟩
```

A regra diz que _se um operador `+` for o próximo token a
processar, o efeito semântico deve ser o equivalente a
desempilhar dois valores e empilhar a soma dos dois._ 

> Observe que o `+` na primeira parte da regra é um operador da
> linguagem que estamos especificando e projetando (de RPN em
> nosso exemplo). Já o operador `+` na linha de baixo é o
> meta-operador (da meta-linguagem; de Python, em nosso exemplo).


### Sucesso e Erros

Quando uma sequência de transições pode ser realizada a partir do
estado inicial `⟨programa, []⟩` (onde `programa` é a sequência de
tokens e `[]` é uma pilha vazia) e essa sequência leva a um
estado final da forma `⟨[], [valor]⟩` (ou seja, em que não há
mais tokens a processar e em que a pilha tem um único `valor`),
dizemos que a computação foi concluída com _sucesso_ e que o
significado de `programa` é `valor`. Caso contrário, se não
houver sequência de transições possível que leve a um estado
dessa natureza, dizemos que o programa tem um erro e que o seu
significado é o próprio erro.
