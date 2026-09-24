# Aula 05 — 23/Set — Estágio 2 (Semana 2)

## Retomando da aula anterior

1. na última aula, vimos como é possível derivar o código do lexer e do parser
   a partir das especificações formais do léxico e da sintaxe da linguagem (em
   REGEX e BNF);

2. para o lexer, funções simples baseadas em expressões regulares permitem
   identificar os tipos de tokens (categorias léxicas);

3. para o parser, as regras da gramática dão origem a um conjunto de funções
   mutuamente recursivas que permitem facilmente derivar _parsers descendentes
   recursivos_ que fazem a verificação da sintaxe de um stream tokens;

4. cada regra é transformada em uma função em pseudo-código que pode ser
   facilmente derivada da BNF; em seguida, cada pseudo-função é transformada em
   código real através de uma transformação mecânica (boilerplate);

5. vejamos como fica o pseudo-código em `pseudo-codigo.md` 
   - em seguida, veja como fica o código final em `mlisp-v4`


## BNFs vs EBNFs

**BNFs** são uma notação extremamente simples. Uma especificação BNF consiste
de um conjunto de terminais, um conjunto de não-terminais e uma série de regras
de produção. Tipicamente, não-terminais são expressos na forma
`<nome-do-não-terminal>`; terminais são expressos em letras maiúsculas e/ou
negrito, sem os `<` e `>` (o importante é que seja fácil diferenciar os dois
tipos de símbolos); por fim, as regras de derivação têm uma formação muito
simples: `::=` é usado para introduzir a regra de derivação de um não-terminal;
do lado direito, uma sequência de símbolos (terminais e não terminais)
especifica como derivar uma instância do não-terminal (uma _frase_, poderíamos
dizer); por fim, BNF permite especificar produções através de alternativas (com
o operador `|`) e recursões (um não-terminal pode referenciar a si próprio na
produção); há também, tipicamente, algum símbolo para representar uma produção
vazia. Isso é tudo que existe na BNF clássica introduzida por Backus e Naur
para a especificação de Algol 60.

**EBNFs** é uma família de meta-linguagens alternativas a BNF que introduzem
elementos adicionais na notação, para facilitar a escrita de gramáticas. O uso
de EBNFs torna as gramáticas, ao mesmo tempo, mais sucintas e mais legíveis. E,
por fim, torna mais perceptível uma implementação mais direta, já que
evidenciam como usar laços iterativos em vez de chamadas recursivas para as
repetições nas produções.

Quais elementos, EBNFs introduzem? Na prática, isso varia bastante entre as notações concretas usadas pelos diferentes projetos. Mas alguns elementos são bastante comuns:

- `X+`: indica que `X` pode ser repetido 1 ou mais vezs
- `X*`: indica que `X` pode ser repetido 0 ou mais vezs
- `( … )`: permite tratar `…` como um grupo (pra aplicar outras operações)
- `[ … ]`: indica que `…` é opcional;
- `{ … }`: indica que `…` pode ser repetido;

Estes operadores tornam as especificações em EBNFs menores que as equivalentes
em BNF. Repetições e opcionais normalmente requerem regras intermediárias ou
produções alternativas em BNF. Em EBNFs repetições e opcionais podem ser
expressas com facilidade e boa legibilidade, diretamente nas sequências de
símbolos de cada regra de produção. Veja, por exemplo, como a gramática de
mlisp pode ser expressa com uma única regra em EBNF.

```python
<s-expressao> ::= LPAREN OPERADOR { INTEIRO | <s-expressao> } RPAREN"""
```

Tente ler a regra acima. Ela expressa de forma bastante natural o que é uma
s-expressão de mlisp: é uma sequência iniciada por um `LPAREN` e um `OPERADOR`;
seguida por uma parte opcional que pode ser ou um `INTEIRO` ou uma outra
`<s-expressão>` inteira; e, por fim, concluída sempre por um `RPAREN`. Observe
que o uso de `{` e `}` permite evitar o não-terminal `<argumentos>` e sua regra
intermediária (e também o do não-terminal `arg`).

Some a isso que o código que pode ser derivado é bastante intuitivo. Precisamos
apenas usar `expect()` para os dois primeiros terminais; em seguida, precisamos
de um loop `while` que deve ler um `INTEIRO` ou uma `<s-expressão>`; entramos e
permanecemos no loop enquanto não encontrarmos  um `RPAREN` no stream; ao
sairmos do loop, usamos `expect()` pela última vez, para consumir o terminal
`RPAREN` que conclui a `<s-expressao>`. Veja o pseudo-código abaixo.

```python
def parse_s_expressao(stream):
    expect(LPAREN)
    op = expect(OPERADOR)
    args = []
    while not RPAREN(stream.peek()):
        if peek(INTEIRO):
            args.append(expect(INTEIRO))
        else:
            args.append(parse_s_expressao(stream))

    expect(RPAREN)
    return [op, *args]
```

E isso é tudo que precisamos para nosso parser.


## Nossa nova linguagem: calc

- linguagem infixa para expressões aritméticas
- adicionaremos um único operador a mais `**` (exponenciação)
- ainda vamos manter a LP tratando apenas inteiros, por simplicidade

Nossas duas linguagens até agora nos permitiram escrever qualquer expressão
aritmética. Ambas, contudo, obrigam o programador a expressar explicitamente a ordem das operações em vez de permitir as expressões convencionais com as quais estamos acostumados. 

A linguagem `calc` que vamos introduzir agora resolverá essa questão
definitivamente. Ela nos permitirá escrever expressões aritméticas usando a
exata forma com a qual estamos acostumados desde o ensino fundamental. A ideia
é que nossa LP possa avaliar expressões como essas abaixo:

- `1 + 2`
- `2 + 3 + 4`
- `2 * 3 + 4`
- `2 ** 3 * 5`
- `2 ** 3 ** 2`
- `1 + (2 * 3)`

## Aspectos importantes a considerar com a notação infixa

### Aridade

O primeiro problema que surge quando adotamos uma notação infixa é o da aridade
das operações. Em princípio, a notação infixa exige que apenas dois valores
sejam operados. Então, como podemos escrever o equivalente à expressão mlisp
`(+ 1 2 3 4)` em calc? A solução é usar mero encadeamento de operações: `1 + 2
+ 3 + 4`.

Mas qual é a sintaxe abstrata por trás dessa expressão? Qual a AST que deve ser
construída? É desse problema que surge uma segunda propriedade importante:
_associatividade_. Observe abaixo que há, em princípio, duas ASTs que podem
corresponder à mesma expressão.

```
  (1 + 2) + 3              1 + (2 + 3)
        +                     +
       / \                   / \
      /   \                 /   \
     +     3               1     +
    / \                         / \
   /   \                       /   \
  1     2                     2     3
```

Qual delas deve ser gerada pelo analisador sintático de nossa LP? É nesse
contexto que surge a propriedade denominada de _associatividade_.

### Parênteses

O problema acima poderia ser facilmente resolvido se obrigássemos o programador
a usar parênteses ao redor de toda operação binária. Isso é exatamente o que
fazemos em `mlisp`, mas é também exatamente o que queremos evitar em `calc`.

O foco agora é fazer a LP mais expressiva e torná-la mais fácil de compreender
e de escrever para o programador da LP, não para o projetista da LP e do
programador do tradutor (seja interpretador ou compilador).

Por isso, para que a notação infixa permita a omissão de parênteses como
fazemos na notação matemática convencional, precisamos definir certas
propridades na linguagem que permitam o correto funcionamento do analisador
sintático e do avaliador.

### Associatividade

Associatividade é a propriedade dos operadores de uma LP que determina como
devem ser feitos os agrupamentos dos operadores de expressões que encadeiam
múltiplos uso do mesmo operador. Como vimos acima, a _associatividade_ de
operadores é uma decisão de _design_ que determina, essencialmente, se o
operador será tratado como associativo à esquerda ou à direita. Cabe ao
projetista da LP determinar como se associam.

Cada operador da LP deve ser considerado separadamente. E a decisão, embora
esteja ocorrendo em nível de sintaxe (estamos tratando do mapeamento de sintaxe
concreta para sintaxe abstrata) precisará considerar propriedades das operações
(nível semântico). Para perceber isso com mais clareza, considere a decisão
sobre a associatividade dos operadores de nossa linguagem. Para cada operação,
considere a expressão genérica `a ⊕ b ⊕ c` (obviamente, substitua o operador
pelo que estivermos considerando)

- `+`: a operação de soma é indiferente à ordem em que as operações são
  executadas; podemos executar `(a + b) + c` ou `a + (b + c)`; logo, podemos
  estabelecer que o operador será associativo à esquerda ou à direita;
  deixaremos pra decidir isso mais adiante, com base em outros critérios;

- `*`: o mesmo se aplica para a operação de multiplicação;

- `-`: aqui a situação é bastante diferente; o resultado da avaliação a partir
  das duas possíveis ASTs, em geral, vai produzir resultados diferentes;
  compare em qualquer LP, os valores de `(a - b) - c` e de `a - (b - c)` com
  valores arbitrários; observe que a escolha convencional é considerar `-` um
  operador com associatividade à esquerda;

- `/`: o mesmo se aplica para a operação de divisão; a associatividade, tal
  como ocorre com `-`, é à esquerda;

- `**`: por fim, considere a operação de exponenciação; observe que este
  operador é, em geral, definido como associativo à direita; ou seja, a sintaxe
  abstrata de `a ** b ** c` deve ser `a ** (b ** c)`; faremos, portanto, o
  mesmo em `calc`;

### Precedência

Agora que já resolvemos a ordem em que expressões com sequências de operadores
iguais serão mapeadas para a representação da sintaxe abstrata, podemos passar
a outro problema: o que devemos fazer quando **operadores diferentes** são
usados em sequência em uma expressão? Em outras palavras, qual deve ser a
sintaxe abstrata de uma expressão genérica na forma `a ⊕ b ⊞ c`

- `a ⊕ b ⊞ c`  --> `(a ⊕ b) ⊞ c`
- `a ⊕ b ⊞ c`  --> `a ⊕ (b ⊞ c)`

Observe que aqui não podemos usar a propriedade de associatividade porque não
se trata de um mesmo operador: são dois operadores distintos `⊕`  e `⊞` (lembre
estes são apenas símbolos genéricos, tipicamente usados quando tratamos de
linguagens ou notações, para nos referirmos a operadores quaisquer).

A solução para isso é uma nova tomada de decisão que ordena os operadores em classes de _precedência_. Acredito que a precedência de operadores matemáticos são fáceis de você recordar do ensino médio e fundamental. De toda forma, seguem as precedências convencionalmente usadas.

- baixa: `-` e `+`
- média: `*` e `/`
- alta: `**`

Observe que uma categorização de precedências obriga o projetista da linguaggem
a considerar as relações entre todos os operadores que a LP proporciona, porque
se trata de uma propriedade da relação entres os operadores. Compare isso com a
propriedade da associatividade que é uma propriedade de cada operador
individualmente.

### Uma observação sobre rpn e mlisp

Relembre nossas duas linguagens anteriores. Observe como a sintaxe concreta
evitava os problemas acima intencionalmente. A própria escrita obrigava o
programador a decidir a ordem das operações, sem a necessidade de decisões de
associatividade ou de precedência para a criação das ASTs.


## Gramáticas, aridade, associatividade e precedência

Mas como podemos garantir que a sintaxe abstrata correta seja produzida para
cada expressão? A resposta para isso está na escrita das regras da gramática.

A precedência define qual operador "liga mais forte", ou seja, qual
subexpressão deve ser agrupada primeiro. Na AST, operadores de maior
precedência precisam aparecer mais próximos das folhas, enquanto operadores de
menor precedência devem ficar mais próximos da raiz (confira as árvores que
desenhei no início do texto). A gramática, portanto, precisa refletir isso por
meio de uma hierarquia dos não-terminais: expressões de menor precedência podem
conter expressões de maior precedência, mas não o contrário. Se observarmos
isso, o próprio formato das produções forçará o parser a construir a subárvore
correta antes de aplicar o operador mais fraco.

A associatividade define como operadores de mesma precedência se agrupam (*). A
associatividade também é codificada na forma das regras de produção. Se a
recursão de um nível da gramática "puxa" para a esquerda, a AST tende a ficar
associativa à esquerda; se "puxa" para a direita, associativa à direita. Isso
não é um detalhe de implementação do parser: é uma decisão de projeto da
gramática e da LP, portanto. Uma gramática bem escrita deixa explícito se uma
sequência de operadores iguais deve ser agrupada da esquerda para a direita, da
direita para a esquerda, ou se tal sequência é proibida.

> (*) Um detalhe aqui. Na prática, é comum definimos associatividade para grupos de
> operadores que estão na mesma categoria de precedência. Assim, por exemplo,
> definimos as regras de associatividade

A aridade também aparece nesse projeto. As produções determinam quantos
operandos cada construtor sintático espera e como eles se combinam. Um operador
binário, por exemplo, precisa de uma produção que relacione dois componentes;
um operador unário, de uma produção que relacione apenas um. Se o operador for
ternário, precisa explicitamente exigir sintaxe que permita a derivação correta
da AST que represente toda a operação. A AST só terá os nós com a aridade
correta se a gramática tiver produções que expressem isso sem ambiguidade. 

Se a gramática for ambígua, uma mesma sentença poderá admitir mais de uma
árvore de derivação. Nesse caso, a AST pode variar dependendo do parser ou de
regras externas de desambiguação. Isso é indesejável, porque a semântica da
linguagem (avaliação, tipos, geração de código) depende da forma da AST. Como
vimos acima, uma expressão avaliada com o agrupamento errado produz o resultado
errado. Por isso, em geral, buscamos projetar gramáticas não ambíguas ou,
quando isso não é possível, regras explícitas que eliminem a ambiguidade.

Portanto, ao escrever uma BNF, não estamos apenas descrevendo a forma textual
da linguagem. Estamos projetando a forma das ASTs. Precedência, associatividade
e aridade não são propriedades mágicas dos operadores; são propriedades da
gramática. Uma gramática bem projetada faz com que a AST correta seja uma
consequência natural das derivações, sem necessidade de correções posteriores.
É essa disciplina no projeto da LP que garante que os tradutores
(interpretadores ou compiladores) possam confiar nas estruturas produzidas.

### Projeto da sintaxe de `calc`

Considere `calc` com as aridades, associatividade e precedências que
especificamos acima. Abaixo, vamos percorrer uma tentativa de projeto da nossa
nova LP.


#### Primeira tentativa: uma única categoria de expressão

Uma tentação inicial é tratar todas as expressões como um único não-terminal:

```
exp ::= exp + exp | exp - exp | exp * exp | exp / exp | exp ** exp | INTEIRO | ( exp )
```

A aridade está correta: cada produção de operador tem exatamente dois
operandos. A AST teria nós binários para `+`, `-`, `*`, `/` e `**`, e folhas
para inteiros.

O problema é que essa gramática é ambígua. Por exemplo, `2 + 3 * 4` pode ser
derivada como `(2 + 3) * 4` ou como `2 + (3 * 4)`. Da mesma forma, `2 ** 3 **
4` pode ser `(2 ** 3) ** 4` ou `2 ** (3 ** 4)`. A gramática não impõe
precedência nem associatividade; a AST dependeria de escolhas do parser.

#### Segunda tentativa: por precedência, associatividade toda à esquerda

Para impor precedência, o caminho é criar níveis hierárquicos dos
não-terminais. Lembre que a ideia é que expressões com operadores de menor
precedência podem conter expressões com os operadores de maior precedência, mas
não o contrário.

```
exp    ::= exp + termo | exp - termo | termo
termo  ::= termo * fator | termo / fator | fator
fator  ::= fator ** atomo | atomo
atomo  ::= INTEIRO | ( exp )
```

Agora a hierarquia é:
- `exp`: operadores `+` e `-` (menor precedência);
- `termo`: operadores `*` e `/` (precedência intermediária);
- `fator`: operador `**` (maior precedência);
- `atomo`: literais inteiros e expressões entre parênteses.

Observe que assim definida, expressões como `2 + 3 * 4` têm necessariamente
sintaxe abstrata `2 + (3 * 4)`, enquanto `2 * 3 ** 4` terá sintaxe abstrata
igual a `2 * (3 ** 4)`. A precedência, agora, está correta e é imposta pelas
regras da gramática.

Contudo, todas as recursões são à esquerda (`exp ::= exp …`, `termo ::= termo
…`, `fator ::= fator …`). Portanto, todos os operadores ficam associativos à
esquerda. Isso está perfeitamente ok para `+`, `-`, `*` e `/`, mas não para
`**`. Com essa gramática, `2 ** 3 ** 4` seria agrupado como `(2 ** 3) ** 4` que
não é o agrupamento esperado… se o usarmos, a semântica também não será a
esperada.

#### Terceira tentativa: ajustando a associatividade de **

Para tornar o operador `**` associativo à direita, basta mudar a recursão desse
nível imposta pela gramática. Em vez de `fator ::= fator ** atomo | atomo`,
podemos usar:

```
fator ::= atomo ** fator | atomo
```

Observe que agora, a recursão "puxa" para a direita (observe o lado de `fator`
na produção `atomo ** fator` e compare com a regra anterior). Com isso, `2 ** 3
** 4` será agrupado como `2 ** (3 ** 4)`, que é o comportamento convencional e
esperado para potência. Veja que essa mudança não afeta a precedência que
continua a mesma, porque `fator` ainda está abaixo de `termo`, mas acima de
`atomo`.

#### Gramática final

Combinando as decisões acima, chegamos à gramática BNF final para `calc`.
Detalhe, essa é a gramática clássica que é usada em praticamente qualquer LP
moderna para as expressões aritméticas.

```
exp    ::= exp + termo | exp - termo | termo
termo  ::= termo * fator | termo / fator | fator
fator  ::= atomo ** fator | atomo
atomo  ::= INTEIRO | ( exp )
```

Observações importantes quanto a essa gramática:

1. Aridade: cada produção de operador binário tem exatamente dois não-terminais
   de expressão, um à esquerda e um à direita do operador. Isso garante que
   cada nó de operador na AST tenha dois filhos. INTEIRO é uma folha. Os
   parênteses não criam nó na AST; apenas agrupam.

2. Precedência: quanto mais abaixo na hierarquia, maior a precedência. atomo
   tem a maior precedência (parênteses e literais), depois fator (**), depois
   termo (*, /), e por fim exp (+, -).

3. Associatividade: exp e termo são recursivos à esquerda, então `+`, `-`, `*`
   e `/` são associativos à esquerda. fator é recursivo à direita, então `**` é
   associativo à direita.

4. Ambiguidade: essa gramática é não ambígua para a linguagem que estamos
   especificando. Cada expressão válida tem uma única árvore de derivação e,
   portanto, uma única AST.

5. O terminal `INTEIRO` representa literais inteiros. Tal como nas LPs
   anteriores que construímos, a gramática não se preocupa com o tipo do
   resultado; `1 / 2` é sintaticamente válido, ainda que o resultado possa não
   ser inteiro. Essa é uma questão semântica, não sintática.


### Exemplos de derivações sintáticas em `calc`

Em sala de aula discutimos duas derivações: `2 * 3 + 4` e `2 * (3 + 4)`. As
expressões são parecidas, mas na segunda o "programador" usou parênteses para
forçar a execução da soma antes da multiplicação. Ele faz isso porque sabe que
a linguagem da maior precedência à multiplicação. Vejamos cada uma das duas
derivações.

#### calc: sintaxe

Apenas retomando a gramática final adotada.

```
exp    ::= exp + termo | exp - termo | termo
termo  ::= termo * fator | termo / fator | fator
fator  ::= atomo ** fator | atomo
atomo  ::= INTEIRO | ( exp )
```

### Exemplo 1: `2 * 3 + 4`

Em sala de aula, fizemos a derivação, evitando certos passos para tornar o
processo mais rápido. Aqui coloco a derivação completa. Do lado esquerdo você
vê a sequência de derivações e do lado direito a produção que foi usada.

```
exp ⇒ exp + termo            (exp ::= exp + termo)
    ⇒ termo + termo          (exp ::= termo)
    ⇒ termo * fator + termo  (termo ::= termo * fator)
    ⇒ fator * fator + termo  (termo ::= fator)
    ⇒ atomo * fator + termo  (fator ::= atomo)
    ⇒ 2 * fator + termo      (atomo ::= INTEIRO)
    ⇒ 2 * atomo + termo      (fator ::= atomo)
    ⇒ 2 * 3 + termo          (atomo ::= INTEIRO)
    ⇒ 2 * 3 + fator          (termo ::= fator)
    ⇒ 2 * 3 + atomo          (fator ::= atomo)
    ⇒ 2 * 3 + 4              (atomo ::= INTEIRO)
```

Também desenhei as árvores de derivação sintática (também apenas de forma
parcial) e a árvore de sintaxe abstrata. Abaixo seguem as duas árvores lado a
lado (se encontrarem erro, por favor, avisem!). Observe que a AST é
essencialmente a mesma estrutura da árvore de derivação, da qual retiramos os
símbolos não terminais e quaisquer terminais que são sejam relevantes do ponto
de vista semântico (parênteses, no nosso caso).


```
                exp                             +
             /   |   \                        /   \
          exp    +    termo                  *     4
           |            |                  /   \ 
         termo        fator               2     3
        /  |  \         |
   termo   *  fator   atomo
     |          |       |
   fator      atomo     4
     |          |
   atomo        3
     |
     2
```


### Exemplo 2: `2 * (3 + 4)`

```
exp ⇒ termo                       (exp ::= termo)
    ⇒ termo * fator               (termo ::= termo * fator)
    ⇒ fator * fator               (termo ::= fator)
    ⇒ atomo * fator               (fator ::= atomo)
    ⇒ 2 * fator                   (atomo ::= INTEIRO)
    ⇒ 2 * atomo                   (fator ::= atomo)
    ⇒ 2 * ( exp )                 (atomo ::= ( exp ))
    ⇒ 2 * ( exp + termo )         (exp ::= exp + termo)
    ⇒ 2 * ( termo + termo )       (exp ::= termo)
    ⇒ 2 * ( fator + termo )       (termo ::= fator)
    ⇒ 2 * ( atomo + termo )       (fator ::= atomo)
    ⇒ 2 * ( 3 + termo )           (atomo ::= INTEIRO)
    ⇒ 2 * ( 3 + fator )           (termo ::= fator)
    ⇒ 2 * ( 3 + atomo )           (fator ::= atomo)
    ⇒ 2 * ( 3 + 4 )               (atomo ::= INTEIRO)
```

E as árvores de derivação sintática completa e a AST correspondente seguem
abaixo, para esta segunda expressão.

```
           exp                             *
            |                            /   \
          termo                         2     +
       /    |    \                          /   \
   termo    *    fator                     3     4
     |             |
   fator         atomo
     |         /   |   \
   atomo      (   exp   )
     |           / | \
     2         exp + termo
                |      |
              termo  fator
                |      |
              fator  atomo
                |      |
              atomo    4
                |
                3
```

Compare as duas árvores abstratas resultantes. A expressão `2 * 3 + 4` tem a
sintaxe abstrata representada pela primeira AST porque a gramática da linguagem
dá maior precedência ao operador `*` que ao `+`. E isso ocorre porque a
multiplicação é derivada em um nível mais profundo na hierarquia das regras de
produção. É a hierarquia que obriga a derivar as operações de adição e
subtração antes das operações de multiplicação e divisão. E estas antes da
operação de exponenciação. Já a segunda AST é derivada como representação da
expressão `2 * (3 + 4)` porque a regra que introduz os parênteses (com uma
subexpressão) está no nível mais profundo da gramática. Isso garante que ela
tenha maior precedência que qualquer outra operação. E, de fato, isso é o que
precisamos, já que os parênteses em `calc` têm exatamente o papel de dar ao
programador o poder de forçar a ordem de operações como ele quiser.


#### Exercícios de fixação (sem necessidade de entrega)

1. Quais seriam as consequências se tivéssemos usado as regras abaixo para
   definir `fator` em vez da regra que escolhemos:

   a) `fator ::= fator ** atomo | atomo`
   b) `fator ::= atomo ** atomo | atomo`

   > Dica: tente encontrar expressões que vão produzir derivações diferentes para
   > as regras originais e para as propostas.

2. Tente implementar um parser descendente recursivo a partir das regras de
   derivação das funções que vimos no início da aula. Explique os problemas que
   encontrar ao fazer essa tentativa.

3. Abaixo segue uma regra que pode ser usada para transformar uma regra de
   produção escrita em BNF para uma equivalente escrita em EBNF. Explique: a)
   por que essa regra é válida? e b) qual benefício há na regra resultante em
   comparação com a regra original?

   ```
   [BNF]    A ::= A x | A y | z
            ==>
   [EBNF]   A ::= z { x | y }
   ```

4. Partindo das regras de produção de `calc` escritas em BNF apresentadas
   acima, reescreva as regras usando a notação EBNF, aproveitando os operadores
   de opcionais e de repetições. Dica: use a regra de reescrita do exercício
   anterior, se for possível.
