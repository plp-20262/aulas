# Aula 06 — 28/Set — Unidade 2 (4/4)

## Retomando da aula anterior

1. na aula anterior, vimos como podemos derivar mecanicamente um parser (do
   tipo descendente recursivo) a partir das regras de uma gramática BNF; usamos
   `mlisp` e `calc` para demonstrar a ideia; vimos também que uma gramática
   EBNF permite escrever regras menores e mais simples (com menos não-terminais
   que uma BNF equivalente) e que podem ser implementadas combinando recursão e
   iteração (mapeando condicionais a `if`s e as repetições a laços `while`);

2. em seguida, revisitamos os conceitos de aridade, associatividade e

   precedência que já conhecíamos da matemática de ensino fundamental e médio;
   com base nisso, projetamos a gramática de `calc`; vimos que as três
   propriedades podem ser diretamente codificadas em uma gramática BNF e que
   fazer isso garante que as derivações e as ASTs produzidas já refletirão as
   propriedades, preparando o passo semântico;

   > vale relembrar aqui que precedência é condificada, introduzindo níveis de
   > hierarquia entre os não-terminais; a associatividade é codificada usando
   > recursividade do mesmo lado desejado para a associatividade; e a aridade é
   > codificada pelo próprio sequenciamento dos terminais e não-terminais nas
   > regras de produção;

3. no final da aula, através de exercícios de fixação, desafiei os alunos a
   escrever um parser para `calc` a partir da gramática apresentada, usando a
   abordagem apresentada antes (e que exemplifiquei escrevendo a última versão
   do parser de `mlisp`); ou seja, derivando um parser descendente recursivo a
   partir das regras de produção da gramática;

   > a aula será retomada a partir desse exercício
   >
   > se os alunos não tiverem feito o exercício, talvez valha a pena usar como
   > um pequeno "miniteste" escrito no início da aula

## Recursividade à esquerda

(material novo da aula: começar fazendo o exercício pedido)

### façamos o pseudo-código do parser de `calc`

(ver Tentativa 1 no arquivo `./calc-v1/README.md`)


### transformações de gramáticas

- a escolha do lado em que colocamos a recursividade nas regras de
  produção determina o lado da associatividade dos respectivos operadores;

- mas agora percebemos que a recursividade à esquerda é um problema
  para a derivação das funções que implementam um parser descendente recursivo;

- o fato é que há várias situações em que é necessário ajustar a gramática para
  torná-la mais apropriada para certos propósitos; um deles é poder implementar
  parsers recursivos descendentes; para esse fim, em geral, três transformações
  costumam ser suficientes;

#### eliminação de produções vazias

- produções vazias `A ::= ε` são essencialmente _incômodas_ para manipular em
gramáticas BNF;

- na prática, implicam em não-terminais que podem ser anulados em derivações;
de uma sequência contendo o não-terminal que tem uma produção vazia pode se
derivar a mesma sequência em que o não-terminal é anulado: `α A β` => `α β`;

- em alguns casos, pode implicar em conflitos para a escrita do parser: por
exemplo, em `A ::= ε | B`, se o próximo símbolo pode iniciar `B` ou ou seguir
`A` não saberemos qual produção expandir;

- além desses motivos, há alguns outros pelos quais é conveniente eliminar
  produções vazias para usar gramáticas; felizmente, é algo bastante simples de
  fazer; considere a situação abaixo:

```python
A ::= ε | a
B ::= b A c
```

- observe que nessa gramática, o objetivo do não-terminal `A` é essencialmente,
  permitir que o terminal `a` seja opcional;

- se quiséssmos manter a notação em BNF, essa remoção exige eliminar a produção
vazia e, portanto, garantir que sempre que `A` esteja na sequência de
derivação, ela produza um `a`; mas, além disso, é necessário introduzir novas
regras para os casos em que o `A` deveria ser anulado;

```python
A ::= a
B ::= b A c | b c
```

- ao usarmos EBNF, a transformação é ainda mais clara e simples, já que podemos
  usar o operador de opcionalidade para esse fim, ao redor de cada `A` nas
  demais regras;

```python
A ::= a
B ::= b [ A ] c
```

ou até… (nesta opção, eliminamos uma regra que produz apenas um símbolo)

```python
B ::= b [ a ] c
```

#### eliminação de recursões à esquerda

- este é mais um caso com que nos deparamos na gramática de `calc`;

- o terceiro exercício da aula passada indicava a solução para o desafio:
  uma regra de reescrita de regras de produção que permite produzir novas
  regras de produção equivalentes às originais, mas que eliminam a necessidade
  de recursão a esquerda; a regra apresentada lá é a seguinte:

   ```python
   A ::= A x | A y | z          # regra original em BNF
   ==>
   A ::= z { x | y }            # regra resultante em EBNF
   ```

- primeiro, reflita sobre a regra de produção original: ela expressa que o
  não-terminal `A` tem três regras de produção: `A x`, `A y` e `z`;

- derive algumas strings a partir de `A`, manualmente; a menor string que pode
  ser derivada é `z`, usando a produção 3; depois dela, fica fácil perceber que
  também podemos derivar `z x` e `z y`, aplicando as produções 1 e 2,
  respectivamente; depois, teremos `z x x` e `z x y`; e assim por diante;

- agora releia o que a regra resultante expressa: ela diz que o não-terminal
  `A` tem uma única regra de produção `z { x | y }` que expressa que são
  palavras iniciadas por um `z`, seguidas por repetições de `x | y`; ou seja,
  repetições de ou `x` ou `y`;

- não é difícil ver que são, de fato, equivalentes; o que ocorre é que a função
  das produções na BNF original são bem específicas: a produção 3 dá o ponto de
  partida, já que só tem terminais; e as produções 1 e 2 diz como aumentar a
  palavra; 

  essa regra de transformação, na verdade, não se limita a quando temos apenas
  três produções; a forma mais geral dessa regra de transformação costuma ser
  expressa como indico abaixo:

  ```python
  A ::= A α₁ | ... | A αₘ | β₁ | ... | βₙ                  # em BNF
  ==>
  A = ( β₁ | β₂ | ... | βₙ ) { ( α₁ | α₂ | ... | αₘ ) } ;  # em EBNF
  ```
  
  Onde `A` é um não-terminal e onde os `α` e `β` são sequências de símbolos da
  gramática. Observe que estou usando EBNF para expressar a regra resultante,
  mas seria perfeitamente possível usar BNF pura para as transformações.
  Infelizmente, iria requerer o uso de uma regra intermediária para isso.

> Sei que pode ser difícil ler notação formal. Se você tiver essa dificuldade
> (e todos têm no começo), pense em casos concretos, com poucos elementos
> envolvidos. Como o primeiro exemplo de transformação que eu dei acima. Tente
> generalizar de lá e produza você mesmo uma regra em que haja duas
> possibilidades de regras só com terminais e pense como a transformação
> deveria ser. Em seguida, compare com a regra geral. Se ainda não estiver
> claro, dê mais um passo concreto e introduza uma regra para 3 recursões à
> esquerda.

#### fatoramento à esquerda

- esta é outra situação bastante corriqueira quando manipulamos gramáticas BNF:
  várias produções têm prefixos semelhantes;

- quando há múltiplas produções têm um mesmo prefixo, é conveniente fatorá-las à
  esquerda; isso evita a necessidade de escolher entre diferentes produções antes
  de que a decisão seja possível;

- (de fato, às vezes é conveniente fazer procedimento semelhante com sufixos, à
  direita, portanto)

- a regra de fatoramento à esquerda é expressa da seguinte forma:

```python
A  ::=  α β₁ | α β₂ | ... | α βₙ | γ        # original em BNF

==>

A  ::=  α A′ | γ                            # resultante em BNF
A′ ::=  β₁ | β₂ | ... | βₙ

==>

A ::= α ( β₁ | β₂ | ... | βₙ ) | γ ;        # resultante em EBNF
```

- acima mostro primeiro a resultante em BNF (que impõe a adição de uma regra
  intermediária para lidar com as alternativas); e no final a versão em EBNF
  que é bem mais clara;

- o nome da regra de transformação devem lembrar você do que chamamos
  de _fatoramento_ em expressões algébricas convencionais; é boa analogia;

- como o `α` se repete como prefixo em várias produções, o trecho é _fatorado_;
  observe que ele é colocado no início da regra resultante e não aparece mais
  dentro do agrupamento que se segue `( β… | … )`;

- a título de aplicação, veja como isso se aplica a uma sintaxe que você
  certamente conhece de outras LPs;

```python
S  ::=  if E then S |  if E then S else S |  outro
```

  se precisarmos fazer o `parse_S()` dessa regra, precisamos saber se haverá ou
  não o `else` no stream; talvez pudéssemos considerar fazer isso, olhando 5
  tokens à frente, mas isso é inconveniente e nos afasta do objetivo de fazer a
  gramática e o parser serem LL(1);

- é aí que podemos aplicar a regra em questão: a regra diz é que a sequência
`if E then S` que é prefixo à esquerda de duas das produções pode ser fatorado,
resultando nas duas regras abaixo:

```python
S  ::=  if E then S S' | outro
S' ::=  else S | ε
```

- e se aplicamos a eliminação da produção vazia teremos:

```python
S  ::= if E then S [ S' ] | outro
S' ::= else S
```

- que podemos ainda simplificar para

```python
S  ::=  if E then S [ else S ] | outro
```

#### outras transformações

Diversas outras transformações em gramáticas são possíveis e estão catalogadas
em diversos artigos e livros de projeto de linguagens de programação, de
compiladores e de teoria da computação. Sempre que você se deparar com
situações anôma-las em compreender uma gramática (ou parte dela) considere
pensá-la em um formato diferente, usando transformações para o raciocínio.

Uma forma de pensar em transformações de gramáticas é encará-las como você
encara transformações e refatoramentos de código. Em particular, observe que,
em geral, queremos que as transformações mantenham certas propriedades e mudem
outras, tal como ocorre com transformações e refatoramentos de código.

> Lembre que, no fim das contas, gramáticas são essencialmente especificações
> de muito alto nível de analisadores sintáticos (e que, por sinal, podem
> incluir certas ações semânticas).

### agora, podemos refazer o pseudo-código do parser de `calc`

(ver Tentativa 2 no arquivo `./calc-v1/README.md`)


