# Aula 20 — 25/Nov — Unidade 8 (1/3): tipos estáticos e a linguagem `church`

> Tema da aula: início da Unidade 8. Vamos descobrir por que queremos
> detectar erros de tipo **antes** de executar um programa, tomar as
> decisões de design de um sistema de tipos e especificar a linguagem
> `church`, que é `aljabr` v3 com anotações de tipo e um verificador
> estático.
>
> - `church` = `aljabr` v3 + anotações de tipo + verificação estática
> - hoje: problema, decisões de design, especificação informal,
>   **léxico**, **sintaxe**, **semântica** (dinâmica e estática, esta
>   última só para literais, operadores, variáveis e `let`)
> - na Aula 21: as regras de tipo para funções, aplicação, `if` e
>   `letrec`, e a leitura do verificador de referência
> - na Aula 22: discussão (tipagem estática × dinâmica) e fecho da unidade
>
> Esta aula segue o **ciclo reduzido** do segundo estágio: problema →
> decisão de design → especificação informal → especificação formal →
> discussão. A implementação **não** é construída em aula: o verificador
> de referência é preparado antes e será lido na Aula 21. Você já tem,
> contudo, tudo o que precisa para tentar escrevê-lo por conta própria
> (ver o mapa de implementação ao final deste texto).

> Uma observação sobre o nome. `church` homenageia o matemático Alonzo
> Church, que em 1940 formulou o **cálculo lambda simplesmente tipado**:
> o cálculo lambda (Aula 14) com um sistema de tipos. É exatamente o que
> faremos com `aljabr`, que é, afinal, uma versão "de curso" do cálculo
> lambda com números e recursão.


## Objetivo geral

Até aqui, todas as linguagens que construímos descobrem erros de tipo
**durante a execução**: somar um número a uma função, aplicar algo que
não é função, usar uma variável que não existe. Em todos esses casos,
a avaliação de um programa acaba em `erro` (ou, pior, em nenhum erro,
como em `2 + (1 < 2)`, que vale `3`).

Hoje investigamos uma pergunta nova:

> **É possível descobrir esses erros antes de executar, apenas olhando
> para o texto do programa?**

A resposta é: sim, para uma certa classe de erros, desde que a
linguagem seja projetada para isso. Um **sistema de tipos estático** é
o conjunto de decisões de design (tipos, anotações, regras) que torna
isso possível. A Unidade 8 inteira é dedicada a ele; hoje ficamos com
a primeira parte:

1. **Decidir** como será o sistema de tipos de `church`.
2. **Especificar** sua sintaxe (léxico e gramática) por completo.
3. **Especificar** as primeiras regras de tipo, com o julgamento
   $\Gamma \vdash e : \tau$.

Um fato importante para o resto da unidade: a **semântica dinâmica**
(as regras de avaliação) de `church` é a mesma de `aljabr` v3. Os tipos
não mudam o que um programa **significa**; eles apenas decidem quais
programas **podem ser executados**.

```text
aljabr v3 ──┬──> aljabr v4   (+ tipos algébricos, `match`)               [Aula 17]
            ├──> algora      (+ estado, comandos, `while`) ──> algora com objetos   [Aulas 15–19]
            └──> church      (anotações + verificador estático)          [Aulas 20–22]
```

> O verificador da Unidade 8 cobre o fragmento **aritmética + variáveis
> + funções** (com `letrec` e `if`), isto é, a linha `aljabr` v3. Ele
> **não** cobre `algora`, objetos nem `match`. Por isso `church` parte
> de v3, e não de v4.


## Roteiro de tempo (≈ 2h)

| Bloco | Conteúdo                                                       | Tempo  |
|-------|----------------------------------------------------------------|--------|
| 1     | Problema: erros de tipo só aparecem na execução                | 10 min |
| 2     | Decisões de design de `church`                                 | 15 min |
| 3     | Especificação informal                                         | 15 min |
| 4     | Especificação formal: léxico, sintaxe, semântica               | 50 min |
| 5     | Discussão                                                      | 20 min |
| 6     | Tabela de síntese                                              | 5 min  |

**Se o tempo apertar** (do corte menos custoso ao mais custoso):
1. a discussão sobre linguagens reais (Bloco 5.3) vai para este texto, sem
   passar pela aula;
2. o Bloco 3 é reduzido à tabela de programas aceitos e rejeitados;
3. a derivação do Bloco 4.5 é feita só com o exemplo aceito.

Não cortar: o Bloco 1 (motivação), as decisões A e B do Bloco 2, as
regras $(\text{T-Var})$, $(\text{T-Let})$ e $(\text{T-Op})$, e a
comparação entre $\Gamma \vdash e : \tau$ e $\langle e, \rho \rangle
\Downarrow v$ (Bloco 5.1).


## Retomando da aula anterior

- **Aula 19** fechou a Unidade 7. Vimos que objetos são closures +
  estado mutável + records, e que objetos e tipos algébricos respondem
  de formas opostas ao problema da expressão. Terminamos observando que
  vários erros que apareceram (a leitura de um campo ausente, o ramo
  `Pot` esquecido, a chamada `alimenta(5, 3)`) só são notados **quando o
  programa executa**.
- **Aula 14** plantou a semente desta unidade: ao decidir como `aljabr`
  v3 expressaria condições, escolhemos que `0` é falso e que as
  comparações devolvem `1` ou `0`. Registramos então que `2 + (1 < 2)`
  passaria a valer `3` e que isso seria "um bom motivo para tipos
  estáticos". Hoje cobramos essa dívida: voltamos à **decisão A** da
  Aula 14.
- **Aula 2** (fim da aula) prometeu uma "terceira forma" de dar
  significado a programas, além do código e da tabela de passos: uma
  forma que **não executa o programa, apenas prevê propriedades dele**.
  É isso que um sistema de tipos faz.


## Bloco 1: Problema — erros de tipo só aparecem na execução (≈ 10 min)

### 1.1 Três programas em `aljabr` v3

Antes de avaliar, pense no resultado de cada programa abaixo.

**Programa (a)**

```text
2 + (1 < 2)
```

<details>
<summary>Qual é o resultado?</summary>

`3`. A comparação `1 < 2` vale `1` (condição numérica, decisão A da Aula
14) e a soma `2 + 1` é perfeitamente válida. **Nenhum erro é
reportado**, embora o programa quase certamente contenha um engano do
programador.
</details>

**Programa (b)**

```text
let soma1 = fn (x) => x + 1 in
soma1(fn (y) => y)
```

<details>
<summary>Qual é o resultado?</summary>

`erro`. O closure `fn (y) => y` não pertence a $ℝ$; o _lift_ de $+$
devolve `erro`. Observe **onde** o erro é descoberto: dentro do corpo
de `soma1`, no momento da chamada, e não no ponto do programa em que o
engano foi cometido (o argumento passado).
</details>

**Programa (c)**

```text
letrec f = fn (n) =>
  if n == 0 then 1 else n + (fn (x) => x)
in
f(0)
```

<details>
<summary>Qual é o resultado? E o de <code>f(1)</code>?</summary>

`f(0)` vale `1`; `f(1)` vale `erro`. O defeito está no programa desde o
início, mas só se manifesta se a execução passar pelo ramo `else`. Se os
testes do programador só exercitarem `f(0)`, o erro **nunca** será
visto.
</details>

### 1.2 O que esses programas têm em comum

| Programa | Quando o problema é notado | Onde é notado                    |
|----------|----------------------------|----------------------------------|
| (a)      | nunca                      | —                                |
| (b)      | na execução                | longe do ponto do engano         |
| (c)      | só se o caminho for executado | depende de quais entradas foram testadas |

Em todos os casos, o defeito **está no texto do programa**: não depende
de nenhum valor de entrada. Se a diferença entre `Num` e função (ou
entre número e resultado de comparação) é uma propriedade do texto,
parece razoável que possa ser verificada **sem executar**.

### 1.3 Pergunta central

> Como projetar uma linguagem de modo que a **maior parte** desses
> erros seja detectada antes da execução, apenas examinando o programa?

### 1.4 O que é um tipo?

Informalmente:

> Um **tipo** é uma classificação de valores. Dizer que uma expressão
> `e` tem o tipo `Num` é prometer que, **se** a avaliação de `e`
> terminar, o valor produzido será um número.

Um **sistema de tipos** é um conjunto de tipos e de regras que associam
tipos a expressões. Chamamos de **estático** o sistema cujas regras são
aplicadas **antes** da execução, apenas sobre o texto do programa.

> Um verificador de tipos é, portanto, uma terceira forma de dar
> significado a um programa (Aula 2): em vez de calcular o **valor** de
> `e`, ele calcula (ou rejeita) o **tipo** de `e`. O que "prevê" é uma
> propriedade do valor, não o valor.


## Bloco 2: Decisões de design de `church` (≈ 15 min)

Mesmo formato das Aulas 9 e 14: alternativas, decisão-alvo, registro.
As decisões A e B são as que mais mudam a linguagem; C e D são
decisões menores, mas que precisam estar registradas.

### 2.1 Decisão A — qual é o tipo de uma comparação?

(Volta à decisão A da Aula 14.)

| # | Opção | Tipos | `2 + (1 < 2)` | Consequências |
|---|-------|-------|---------------|---------------|
| 1 | manter a **condição numérica** de v3 (`0` é falso) | `Num` e tipos de função | aceito (vale `3`) | o verificador não detecta o programa (a) da Aula 14 e do Bloco 1; mudança mínima |
| 2 | **`Bool` distinto de `Num`** | `Num`, `Bool` e tipos de função | **rejeitado** | novos literais; `if` passa a exigir `Bool`; comparações devolvem `Bool` |

**Decisão-alvo: opção 2.** Consequências para a linguagem:

- novo tipo `Bool` e dois literais, `verdadeiro` e `falso`;
- as comparações `==` e `<` têm tipo `Bool`;
- `if` exige condição `Bool` (regra na Aula 21);
- `==` e `<` só se aplicam a `Num` (decisão deliberada: comparar
  `Bool` com `Bool` fica fora; ver exercício 5);
- os nomes `true` e `false` da "biblioteca de booleans" da Aula 12 **não**
  são afetados: usamos nomes em português justamente para não colidir
  com eles. (Aquela biblioteca, aliás, não existe em `church`: ver Bloco
  5.4.)

### 2.2 Decisão B — onde o programador escreve os tipos?

| # | Opção | O que se anota | Exemplo | Observação |
|---|-------|----------------|---------|------------|
| 1 | anotar tudo | parâmetros, retornos e variáveis de `let` | `let x: Num = 1 in …` | verboso, muita redundância |
| 2 | anotar só **onde é necessário** | parâmetros; tipo de retorno do `letrec` | `fn (x: Num) => x + 1` | o resto o verificador calcula |
| 3 | **inferir tudo** | nada | `fn (x) => x + 1` | exige um algoritmo de inferência (Hindley–Milner); fora de escopo |

**Decisão-alvo: opção 2.** Por que exatamente nesses dois lugares?

- **Parâmetros.** Ao verificar o corpo de `fn (x) => …`, o verificador
  precisa saber o tipo de `x`, e nada no texto o determina (em `fn (x)
  => x`, `x` poderia ser qualquer coisa). Logo, o programador diz.
- **Retorno do `letrec`.** No corpo de `fat`, a chamada `fat(n - 1)`
  precisa de um tipo, mas o tipo de `fat` depende do tipo do próprio
  corpo, que é o que estamos tentando calcular. Quebramos o ciclo com
  uma anotação. (Aula 21.)
- **`let` e `fn` comum não precisam de anotação de retorno.** O tipo de
  `e₁` em `let x = e₁ in …` é calculado **antes** de verificar o corpo; e
  o tipo do corpo de um `fn` é calculado a partir de seus parâmetros.

> **Pergunta:** a opção 3 dispensa o programador de escrever qualquer
> tipo. Por que não a adotamos?
> <details>
> <summary>Clique para ver a resposta</summary>
>
> <br>Porque inferência é um **algoritmo** à parte (e um assunto de um
> curso dedicado a tipos), e porque anotar parâmetros tem vantagem
> didática: as anotações são uma **especificação** escrita pelo
> programador, e o verificador a confere. Dizer "esta função recebe um
> `Num`" é uma pequena promessa de interface (ligue com o que
> discutimos na Aula 19).
> </details>

### 2.3 Decisão C — quando se verifica, e o que fica para a execução?

| # | Opção | Fases | Tipos na execução? |
|---|-------|-------|--------------------|
| 1 | verificar **dinamicamente** (como em v3) | só execução | os valores carregam seu tipo |
| 2 | verificar **antes** da execução e **apagar** os tipos | verificação, depois execução | não existem |
| 3 | verificar antes **e** manter tipos em valores | verificação, depois execução | existem |

**Decisão-alvo: opção 2**, conhecida como **apagamento de tipos**
(*type erasure*). O pipeline ganha uma etapa:

```text
  código fonte
       ↓
   [ lexer ]            ← especificado por REGEX
       ↓
    tokens
       ↓
  [ parser ]            ← especificado por EBNF
       ↓
  AST com anotações
       ↓
[ verificador ]         ← especificado por regras de tipo Γ ⊢ e : τ     ← NOVO
       ↓
 AST aprovada + tipo τ
       ↓
[ interpretador ]       ← especificado por regras de avaliação ⟨e, ρ⟩ ⇓ v
       ↓
   resultado
```

Um programa rejeitado pelo verificador **nunca executa**. Um programa
aprovado executa exatamente como em `aljabr` v3, e o interpretador ignora
as anotações. Esta é uma decisão de **simplicidade**: não precisamos mexer
em nenhuma regra de avaliação.

### 2.4 Decisão D — como se escrevem os tipos de função?

Em `aljabr` as funções têm vários parâmetros e **não** são curricadas
(`fn (x, y) => …`). O tipo precisa dizer quantos argumentos recebe.

| # | Opção | Exemplo (função de dois números para número) |
|---|-------|----------------------------------------------|
| 1 | seta entre tipos, como em ML/Haskell | `Num -> Num -> Num` (sugere currying) |
| 2 | **lista de tipos dos parâmetros** e seta | `(Num, Num) -> Num` |

**Decisão-alvo: opção 2**, que espelha `fn (x, y) => …` e deixa a
aridade explícita. A lista de parâmetros é **sempre** parentesada
(mesmo com um parâmetro ou nenhum): `(Num) -> Num`, `() -> Bool`.

### 2.5 Registro

```text
Decisão (A): Bool distinto de Num; comparações devolvem Bool; `if` exige Bool
Decisão (B): anotações obrigatórias nos parâmetros; tipo de retorno obrigatório no letrec; sem inferência
Decisão (C): verificação estática antes da execução; tipos apagados na execução
Decisão (D): tipos de função (τ₁, …, τₙ) -> τ, com a lista sempre entre parênteses
Dívidas técnicas: polimorfismo; inferência; recursão mútua; comparação de Bool; múltiplos erros por execução do verificador
```


## Bloco 3: Especificação informal (≈ 15 min)

### 3.1 Os tipos de `church`

| Tipo | O que classifica | Exemplo de expressão |
|------|------------------|----------------------|
| `Num` | números | `2 + 3` |
| `Bool` | `verdadeiro`, `falso` e resultados de comparações | `1 < 2` |
| `(τ₁, …, τₙ) -> τ` | funções de `n` argumentos | `fn (x: Num) => x + 1` |

Exemplos de tipos de função:

| Tipo | Lê-se |
|------|-------|
| `(Num) -> Num` | recebe um número e devolve um número |
| `(Num, Num) -> Bool` | recebe dois números e devolve um `Bool` |
| `() -> Num` | não recebe argumentos e devolve um número |
| `((Num) -> Num, Num) -> Num` | recebe uma função de `Num` em `Num` e um número, e devolve um número |
| `(Num) -> (Num) -> Num` | recebe um número e devolve **uma função** de `Num` em `Num` |

### 3.2 Como é um programa de `church`

```text
let dobro = fn (x: Num) => x * 2 in
dobro(21)
```

```text
letrec fat = fn (n: Num) : Num =>
  if n == 0 then 1 else n * fat(n - 1)
in
fat(5)
```

```text
let twice = fn (f: (Num) -> Num) => fn (x: Num) => f(f(x)) in
twice(fn (n: Num) => n + 1)(0)
```

Compare com `aljabr` v3: o programa é o mesmo, com duas diferenças:
os **parâmetros** vêm com tipo (`x: Num`) e o `letrec` ganha o tipo do
**retorno** (`: Num`, depois dos parênteses). `let`, `if`, aplicações e
operadores não mudam.

### 3.3 O que o verificador examina

Em linguagem natural, o verificador:

1. atribui `Num` a todo literal inteiro e `Bool` a `verdadeiro` e `falso`;
2. atribui a uma variável o tipo com que foi **declarada** (como
   parâmetro) ou **calculada** (em um `let`); variável não declarada é
   erro;
3. em `let x = e₁ in e₂`, calcula o tipo de `e₁`, usa-o para `x` ao
   verificar `e₂` e devolve o tipo de `e₂`;
4. exige operandos `Num` nos operadores aritméticos, que devolvem `Num`;
5. exige operandos `Num` em `==` e `<`, que devolvem `Bool`;
6. *(Aula 21)* confere funções, aplicações (aridade e tipos dos
   argumentos), `if` (condição `Bool`; ramos de mesmo tipo) e `letrec`.

### 3.4 O que o verificador promete e o que não promete

**Promete** (informalmente): se o programa for aprovado, **não ocorrerão
na execução** os erros abaixo.

| Erro dinâmico de `aljabr` v3 | Onde aparecia | Em `church` |
|------------------------------|---------------|-------------|
| variável não vinculada (`ρ(x) = erro`) | (Var) com $\rho$ _lifted_ | evitado: aqui, não há tipo para `x` |
| operação aritmética ou comparação com valor que não é número | _lift_ de $f_{\text{op}}$ | evitado por (T-Op) |
| aplicar algo que não é função | (AppNaoFuncao) | evitado *(Aula 21)* |
| número errado de argumentos | (AppAridade) | evitado *(Aula 21)* |
| `if` com condição que não é número | (IfCond) | evitado *(Aula 21)* |

**Não promete:**

- que o programa **termina** (`letrec f = fn (n: Num) : Num => f(n) in f(1)`
  é bem tipado);
- que **não haverá `erro`** por operações parciais: `1 / 0` é bem tipado
  (`Num`) e vale `erro`;
- que o programa **faz o que o programador quer**: `fn (x: Num) => x + 2`
  em vez de `x * 2` também é aceito.

> Em linguagem técnica, o que a primeira lista descreve é a **segurança
> de tipos** (*type soundness*): "programas bem tipados não dão erro de
> tipo". Provar essa propriedade está **fora do escopo** do curso. Aqui,
> apenas a enunciamos e a usamos como critério de projeto.

**Efeito colateral inevitável: o verificador é conservador.** Ele só
raciocina sobre o texto, e por isso **rejeita programas que executariam
sem erro**. Por exemplo (com a regra de `if` da Aula 21):

```text
if verdadeiro then 1 else 2 + verdadeiro
```

Nenhuma execução chegaria ao `else`, mas o verificador examina os dois
ramos e rejeita o programa. Isso é o preço de decidir **antes** de
executar: não existe um verificador que aceite exatamente os programas
que não dão erro (é uma consequência de resultados clássicos de
computabilidade que você verá em outras disciplinas). O que projetamos é
um compromisso: rejeitar "um pouco demais" para nunca aceitar "de
menos".

### 3.5 Programas aceitos e rejeitados (parte desta aula)

| Programa | Resultado da verificação | Por quê |
|----------|--------------------------|---------|
| `42` | `Num` | literal |
| `verdadeiro` | `Bool` | literal |
| `2 + 3 * 4` | `Num` | operações aritméticas sobre `Num` |
| `1 < 2` | `Bool` | comparação |
| `let x = 2 + 3 in x < 10` | `Bool` | `x : Num`, depois a comparação |
| `let x = 1 in let x = x < 2 in x` | `Bool` | o segundo `x` **sombreia** o primeiro, e tem tipo diferente |
| `2 + verdadeiro` | **erro de tipo** | `+` espera `(Num, Num)` e recebeu `(Num, Bool)` |
| `(1 < 2) + 1` | **erro de tipo** | é o programa (a) do Bloco 1: agora rejeitado |
| `1 < verdadeiro` | **erro de tipo** | `<` só compara números |
| `verdadeiro == verdadeiro` | **erro de tipo** | decisão A: `==` só para `Num` |
| `-verdadeiro` | **erro de tipo** | `-` unário espera `Num` |
| `(1 < 2) < 3` | **erro de tipo** | `Bool < Num` (a sintaxe aceita; veja `1 < 2 < 3` no Bloco 4.2) |
| `x + 1` | **erro de tipo** | `x` não declarada |
| `(let x = 1 in x) + x` | **erro de tipo** | o `x` do lado direito está fora do escopo do `let` |
| `let x = verdadeiro in x * 2` | **erro de tipo** | `x : Bool` |


## Bloco 4: Especificação formal de `church` (≈ 50 min)

> Como nas Aulas 11 e 14, os parênteses `( … )` da EBNF são
> meta-símbolos; os parênteses da linguagem são `LPAREN` e `RPAREN`.
> Marcamos o que muda em relação a `aljabr` v3 com `← NOVO` e `←
> ALTERADO`.

### 4.1 Léxico (≈ 10 min)

**Novas categorias léxicas:**

```text
COLON      ::=  :                   ← NOVO
TARROW     ::=  ->                  ← NOVO  (seta de tipo)
TNUM       ::=  Num                 ← NOVO
TBOOL      ::=  Bool                ← NOVO
VERDADEIRO ::=  verdadeiro          ← NOVO  (palavra reservada)
FALSO      ::=  falso               ← NOVO  (palavra reservada)
```

**Léxico completo de `church`** (compare com o de `aljabr` v3):

```text
INTEIRO    ::=  [0-9]+
NOME       ::=  [a-z_][a-z0-9_]*       (exceto as palavras reservadas)
LET        ::=  let
IN         ::=  in
FN         ::=  fn
LETREC     ::=  letrec
IF         ::=  if
THEN       ::=  then
ELSE       ::=  else
VERDADEIRO ::=  verdadeiro             ← NOVO
FALSO      ::=  falso                  ← NOVO
TNUM       ::=  Num                    ← NOVO
TBOOL      ::=  Bool                   ← NOVO
POW        ::=  \*\*
ADD        ::=  \+
SUB        ::=  -
MULT       ::=  \*
DIV        ::=  /
EQEQ       ::=  ==
LT         ::=  <
EQUAL      ::=  =
ARROW      ::=  =>
TARROW     ::=  ->                     ← NOVO
COLON      ::=  :                      ← NOVO
COMMA      ::=  ,
LPAREN     ::=  \(
RPAREN     ::=  \)
```

**Palavras reservadas.** Agora são nove: `let`, `in`, `fn`, `letrec`, `if`,
`then`, `else`, `verdadeiro` e `falso`. Nenhuma pode ser nome de variável.
Os nomes de tipo `Num` e `Bool` começam com maiúscula e, por isso, **nunca
casam com `NOME`**; eles são categorias léxicas próprias. Como sempre, a
reserva vale para o lexema **inteiro**: `verdadeiro1` e `falsos` são
`NOME`s válidos; `Numero` e `Foo` não são nada (erro léxico), porque
palavras iniciadas por maiúscula só existem se forem `Num` ou `Bool`.

> **Pergunta (ordem das regras, mais uma vez):** que pares de tokens
> compartilham prefixo agora? Em que ordem devem ser tentados?
> <details>
> <summary>Clique para ver a resposta</summary>
>
> <br>Os mesmos de antes (`**` antes de `*`; `==` e `=>` antes de `=`) e um
> novo: **`->` antes de `-`**. Se `SUB` vier primeiro, o programa `fn (f:
> (Num) -> Num) => …` é tokenizado com um `-` e um `>` solto, o que dá
> erro léxico num programa válido.
> </details>

**Exemplo de tokenização.** O programa `fn (f: (Num) -> Bool) => f(1)`:

| Lexema | Categoria |
|--------|-----------|
| `fn`   | `FN`      |
| `(`    | `LPAREN`  |
| `f`    | `NOME`    |
| `:`    | `COLON`   |
| `(`    | `LPAREN`  |
| `Num`  | `TNUM`    |
| `)`    | `RPAREN`  |
| `->`   | `TARROW`  |
| `Bool` | `TBOOL`   |
| `)`    | `RPAREN`  |
| `=>`   | `ARROW`   |
| `f`    | `NOME`    |
| `(`    | `LPAREN`  |
| `1`    | `INTEIRO` |
| `)`    | `RPAREN`  |

Observe que `->` (seta de **tipo**) e `=>` (seta de **função**) são tokens
diferentes: a primeira separa os parâmetros do retorno em um tipo, a
segunda separa os parâmetros do corpo em um lambda.

Como sempre, o léxico não sabe nada sobre tipos: `Num`, `:` e `->` são
apenas palavras da linguagem. Quem sabe que `(Num) -> Bool` é um tipo é o
parser.

### 4.2 Sintaxe concreta (EBNF) (≈ 15 min)

```text
exp     ::= let NOME = exp in exp
          | letrec NOME = fn LPAREN [ params ] RPAREN : tipo => exp in exp     ← ALTERADO
          | fn LPAREN [ params ] RPAREN => exp
          | if exp then exp else exp
          | comp
comp    ::= soma [ ( == | < ) soma ]
soma    ::= termo { ( + | - ) termo }
termo   ::= fator { ( * | / ) fator }
fator   ::= unario [ ** fator ]
unario  ::= [ + | - ] chamada
chamada ::= atomo { LPAREN [ args ] RPAREN }
atomo   ::= INTEIRO | NOME | verdadeiro | falso                                ← ALTERADO
          | LPAREN exp RPAREN
params  ::= param { , param }                                                  ← ALTERADO
param   ::= NOME : tipo                                                        ← NOVO
args    ::= exp { , exp }
tipo    ::= Num | Bool                                                         ← NOVO
          | LPAREN [ tipos ] RPAREN -> tipo
tipos   ::= tipo { , tipo }                                                    ← NOVO
```

Mudanças em relação a `aljabr` v3:

1. `atomo` ganhou os literais `verdadeiro` e `falso`;
2. `params` agora é uma lista de `param`, e cada `param` tem a forma
   `NOME : tipo` (a anotação é **obrigatória**);
3. o `letrec` exige o tipo de retorno entre o `)` e o `=>`;
4. nasceu a categoria sintática `tipo` (com `tipos` auxiliar).

A gramática continua LL(1): o primeiro token de `tipo` (`Num`, `Bool` ou
`LPAREN`) decide a alternativa; `NOME` ou `RPAREN` decidem se existe uma
lista de `params`; `COLON` ou `ARROW` depois do `RPAREN` decidem se estamos
num `letrec` ou num `fn` comum.

**Decisões de design codificadas na gramática** (mesma disciplina da Aula
5):

- **Anotação obrigatória.** Como `params` exige `: tipo` em cada parâmetro,
  `fn (x) => x` **não é** um programa de `church`: é erro **sintático**, e
  não de tipo.

- **Função comum sem anotação de retorno.** Só o `letrec` tem `: tipo` após
  os parênteses. `fn (x: Num) : Num => x` é erro sintático. (É uma dívida
  técnica: seria natural aceitar uma anotação opcional.)

- **Associatividade da seta.** Na regra de `tipo`, o que vem **depois** da
  seta é um `tipo` completo; por isso `->` é associativo à **direita**:

  ```text
  (Num) -> (Num) -> Num      # é (Num) -> ((Num) -> Num)
  ```

  Pelo mesmo motivo, **o lado esquerdo precisa de parênteses**, e não há
  como parentesar um tipo sem seta: `(Num) -> (Num)` é erro sintático,
  porque o segundo `(Num)` seria seguido de `->`. Para dizer "uma função
  que devolve uma função de `Num` em `Num`" escreve-se `(Num) -> (Num) ->
  Num`.

- **Parênteses na posição de parâmetro.** Para passar uma função como
  parâmetro, o tipo é escrito inteiro: `(f: (Num) -> Num, x: Num)`.
  `(f: Num -> Num)` é erro sintático.

- **Sem anotação em `let`.** `let x: Num = 1 in x` é erro sintático: o
  tipo de `x` é calculado pelo verificador a partir de `1`.

- **`comp` continua não associativa**: `1 < 2 < 3` é rejeitado pelo
  **parser**. Já `(1 < 2) < 3` é sintaticamente válido e é rejeitado
  depois, pelo **verificador**.

Programas que o parser deve **rejeitar**:

| Programa | Por quê |
|----------|---------|
| `fn (x) => x` | parâmetro sem anotação |
| `fn (x:) => x` | falta o tipo |
| `fn x: Num => x` | faltam os parênteses dos parâmetros |
| `fn (x: Num) : Num => x` | `fn` comum não tem tipo de retorno |
| `letrec f = fn (n: Num) => n in f(1)` | `letrec` exige o tipo de retorno |
| `let x: Num = 1 in x` | `let` não tem anotação |
| `fn (f: Num -> Num) => f(1)` | lista de parâmetros do tipo sem parênteses |
| `fn (f: (Num) -> (Num)) => f(1)` | depois da seta, falta um tipo completo |
| `fn (x: Foo) => x` | `Foo` não é um tipo (erro **léxico**) |
| `Num` | um tipo não é uma expressão |
| `let verdadeiro = 1 in 2` | `verdadeiro` é palavra reservada |
| `1 < 2 < 3` | `comp` não é associativa |

Programas que o parser deve **aceitar** (mesmo que o verificador, na Aula 21,
rejeite alguns):

| Programa | Observação |
|----------|------------|
| `fn () => 42` | sem parâmetros |
| `fn (f: (Num) -> Num, x: Num) => f(f(x))` | parâmetro de tipo função |
| `fn (g: () -> Bool) => g()` | tipo de função sem parâmetros |
| `fn (x: Num) => fn (y: Num) => x + y` | função que devolve função |
| `letrec f = fn (n: Num) : (Num) -> Num => fn (m: Num) => n + m in f(1)(2)` | retorno de tipo função |
| `verdadeiro(1)` | sintaticamente ok; erro de tipo na Aula 21 |

### 4.3 Sintaxe abstrata

Nós novos ou alterados da AST (parênteses, vírgulas, `:` e setas não
aparecem; as anotações viram **tipos**, que também são árvores):

```text
Bool(valor)                                      -- verdadeiro / falso
Lambda([(x₁, τ₁), …, (xₙ, τₙ)], corpo)           -- agora com tipos nos parâmetros
LetRec(nome, Lambda(params, corpo_fn), τ_ret, corpo)   -- agora com o tipo de retorno
```

e os **tipos** (uma segunda sintaxe abstrata, a dos tipos):

```text
TNum
TBool
TFun([τ₁, …, τₙ], τ)
```

Gramática abstrata de tipos (compare com a de expressões da Aula 11):

```text
τ ::= Num
    | Bool
    | (τ₁, …, τₙ) -> τ            (n ≥ 0)
```

Exemplos de sintaxe concreta → sintaxe abstrata:

| Programa | AST |
|----------|-----|
| `verdadeiro` | `Bool(True)` |
| `fn (x: Num) => x + 1` | `Lambda([("x", TNum)], Add(Var("x"), Num(1)))` |
| `fn (f: (Num) -> Bool) => f(1)` | `Lambda([("f", TFun([TNum], TBool))], App(Var("f"), [Num(1)]))` |
| `fn () => 42` | `Lambda([], Num(42))` |
| `letrec f = fn (n: Num) : Num => n in f(1)` | `LetRec("f", Lambda([("n", TNum)], Var("n")), TNum, App(Var("f"), [Num(1)]))` |

Dois tipos são **iguais** quando são a mesma árvore: mesmos construtores,
mesmos números de parâmetros, parâmetros iguais dois a dois e retornos
iguais. Em `church`, a igualdade de tipos é **estrutural**.

> **Nota de implementação** (Aula 14): é uma boa hora de ter as ASTs e os
> tipos como `dataclass`es. O verificador vai usar `match` sobre os dois.

### 4.4 Semântica dinâmica (a que já temos)

> **Resposta à pergunta que a turma costuma fazer:** os **domínios** e as
> **regras de avaliação** de `aljabr` v3 continuam exatamente os mesmos.

Isso vale porque adotamos o **apagamento de tipos** (decisão C): as
anotações servem ao verificador e **não existem na execução**.

- $\mathrm{Val} = ℝ \cup \mathrm{Clo} \cup \{\mathbf{erro}\}$, sem mudança.
  Não há valores booleanos: `Bool` é um tipo que existe **só no
  verificador**. Em tempo de execução, as comparações continuam devolvendo
  `1` ou `0`, e `if` continua testando "diferente de zero".
- As regras (Num), (Var), (Let), (Op), (Lam), (App), (AppNaoFuncao),
  (AppAridade), (IfVerd), (IfFalso), (IfCond) e (LetRec) valem como estão.
  Basta ler as regras de (Lam), (App) e (LetRec) **ignorando as
  anotações**: o closure de `fn (x: Num) => e` é $\mathsf{clo}((x), e,
  \rho)$, igual ao de `fn (x) => e`.
- O que **precisa** ser dito (e é a única adição) é o significado dos dois
  novos literais. Como `Bool` não existe na execução, eles são `1` e `0`:

$$
\frac{}{\langle \texttt{verdadeiro}, \rho \rangle \Downarrow 1} \quad \text{(Verd)}
\qquad
\frac{}{\langle \texttt{falso}, \rho \rangle \Downarrow 0} \quad \text{(Falso)}
$$

> **Em outras palavras:** executar um programa de `church` é executar o
> programa de `aljabr` v3 que resulta de **apagar** as anotações e
> trocar `verdadeiro` por `1` e `falso` por `0`. Nenhum domínio e
> nenhuma regra de v3 foi alterado; apenas as duas regras acima, que
> são triviais, foram acrescentadas.

Uma consequência que parece estranha à primeira vista:

```text
let x = 5 in x < 10        # tipo: Bool      valor (execução): 1
```

O **tipo** (calculado antes) diz `Bool`; o **valor** (calculado depois) é o
número `1`. Se o interpretador imprimir só o valor, o programador verá
`1`. O programa principal pode usar o tipo que o verificador calculou
para imprimir `verdadeiro : Bool`.

### 4.5 Semântica estática: as regras de tipo (≈ 25 min)

#### Domínios

| Domínio | Descrição |
|---------|-----------|
| $\mathrm{Ty}$ | Tipos: `Num`, `Bool` e `(τ₁, …, τₙ) -> τ` (a gramática abstrata do Bloco 4.3) |
| $\Gamma \in \mathrm{Ctx} = \mathrm{Var} \rightharpoonup \mathrm{Ty}$ | **Contexto de tipos**: associa nomes a **tipos** |

O contexto $\Gamma$ é para tipos o que o ambiente $\rho$ é para valores.
Usamos a mesma notação para estendê-lo: $\Gamma[x \mapsto \tau]$ é o
contexto igual a $\Gamma$, mas em que $x$ tem o tipo $\tau$ (e, como
sempre, **esconde** qualquer associação anterior de $x$). O contexto
inicial é $\emptyset$.

#### O julgamento

$$
\Gamma \vdash e : \tau
$$

Lê-se: *"sob o contexto de tipos $\Gamma$, a expressão $e$ tem tipo $\tau$"*.

Compare com $\langle e, \rho \rangle \Downarrow v$ (Aula 8): lá, a expressão
`e` **avalia para** o valor $v$ sob o ambiente $\rho$; aqui, `e` **tem o
tipo** $\tau$ sob o contexto $\Gamma$. O símbolo $\vdash$ (*turnstile*) é o
mesmo que você viu em Lógica: $\Gamma \vdash A$ lê-se "a partir das
hipóteses $\Gamma$, deduz-se $A$". Aqui as hipóteses são do tipo "$x$ tem
tipo $\tau$".

O julgamento é definido **indutivamente** por regras de inferência, na
mesma notação de Gentzen de sempre. **Se não existe derivação, o programa
é rejeitado.** Dizemos que ele tem um **erro de tipo**.

#### Assinatura dos operadores

Na Aula 7 definimos, para cada operador `op`, uma operação semântica
$f_{\text{op}}$ (e a levamos a $\mathrm{Val}$ com o _lift_). Agora
definimos o **tipo** de cada uma delas: sua **assinatura**.

| Operador `op` | $\mathrm{sig}(\texttt{op})$ |
|---------------|-----------------------------|
| `+` `-` `*` `/` `**` (binários) | $(\mathtt{Num}, \mathtt{Num}) \to \mathtt{Num}$ |
| `==` `<` | $(\mathtt{Num}, \mathtt{Num}) \to \mathtt{Bool}$ |
| `+` `-` (unários) | $\mathtt{Num} \to \mathtt{Num}$ |

> A assinatura de um operador diz, de forma estática, o que $f_{\text{op}}^{\uparrow}$
> faz dinamicamente: onde o _lift_ devolveria `erro` (argumento fora de $ℝ$),
> a assinatura simplesmente **não permite** a combinação.

#### Regras

**Literais.**

$$
\frac{}{\Gamma \vdash n : \mathtt{Num}} \quad \text{(T-Num)}
$$

$$
\frac{}{\Gamma \vdash \texttt{verdadeiro} : \mathtt{Bool}} \quad \text{(T-Verd)}
\qquad
\frac{}{\Gamma \vdash \texttt{falso} : \mathtt{Bool}} \quad \text{(T-Falso)}
$$

**Variável.**

$$
\frac{\Gamma(x) = \tau}{\Gamma \vdash x : \tau} \quad \text{(T-Var)}
$$

Se $x \notin \mathrm{dom}(\Gamma)$, **não há regra aplicável**: variável não
declarada é erro de tipo.

> **Observação.** Na Aula 12, o ambiente $\rho$ era _lifted_: $\rho(x) =
> \mathbf{erro}$ para variáveis não vinculadas, de modo que (Var) cobria
> também esse caso. Aqui **não** fazemos o mesmo com $\Gamma$: o erro não é
> um **tipo** de nenhuma expressão, e sim a **ausência de derivação**.
> (Se $\Gamma(x)$ valesse "erro", a expressão `x + 1` teria algum tipo, e
> perderíamos justamente o que queremos: rejeitá-la.)

**`let`.**

$$
\frac{
  \Gamma \vdash e_1 : \tau_1 \qquad
  \Gamma[x \mapsto \tau_1] \vdash e_2 : \tau_2
}{
  \Gamma \vdash \texttt{let } x = e_1 \texttt{ in } e_2 : \tau_2
} \quad \text{(T-Let)}
$$

Compare com (Let) da Aula 8: a estrutura é **idêntica**. Lá, $e_1$ era
avaliada em $\rho$ e $e_2$, em $\rho[x \mapsto v_1]$. Aqui, $e_1$ é
verificada em $\Gamma$ e $e_2$, em $\Gamma[x \mapsto \tau_1]$. Em particular,
$e_1$ é verificada **sem** $x$ no contexto: o `let` continua não sendo
recursivo.

**Operadores.**

$$
\frac{
  \Gamma \vdash e_1 : \tau_1 \qquad
  \Gamma \vdash e_2 : \tau_2 \qquad
  \mathrm{sig}(\texttt{op}) = (\tau_1, \tau_2) \to \tau
}{
  \Gamma \vdash e_1 \texttt{ op } e_2 : \tau
} \quad \text{(T-Op)}
$$

$$
\frac{
  \Gamma \vdash e : \tau_1 \qquad
  \mathrm{sig}(\texttt{op}) = \tau_1 \to \tau
}{
  \Gamma \vdash \texttt{op } e : \tau
} \quad \text{(T-OpUn)}
$$

> **Leitura de (T-Op).** Para saber o tipo de `e₁ op e₂`, descobrimos o
> tipo de cada operando e **conferimos** se esses tipos casam com a
> assinatura do operador. Se casam, o resultado tem o tipo de retorno da
> assinatura. Se não casam, a terceira premissa **falha** e o programa é
> rejeitado. Um único par de regras cobre os sete operadores binários: a
> diferença entre eles está inteira na tabela de assinaturas.

**O que fica para a Aula 21.** Ainda faltam as regras para $(\text{T-Lam})$,
$(\text{T-App})$, $(\text{T-If})$ e $(\text{T-LetRec})$: as construções
que **criam** e **usam** tipos de função e `Bool` em condições. Elas
completam o sistema de tipos de `church`.

#### Derivação de um programa aceito

`let x = 2 + 3 in x < 10`, com $\Gamma_0 = \emptyset$ e $\Gamma_1 =
\Gamma_0[x \mapsto \mathtt{Num}]$:

```text
∅ ⊢ let x = 2 + 3 in x < 10 : Bool                       (T-Let)
├─ ∅ ⊢ 2 + 3 : Num                                        (T-Op)
│  ├─ ∅ ⊢ 2 : Num                                         (T-Num)
│  ├─ ∅ ⊢ 3 : Num                                         (T-Num)
│  └─ sig(+) = (Num, Num) → Num                           (assinatura)
└─ Γ₁ ⊢ x < 10 : Bool                                     (T-Op)
   │     onde Γ₁ = ∅[x ↦ Num]
   ├─ Γ₁ ⊢ x : Num                                        (T-Var)
   │  └─ Γ₁(x) = Num                                      (acesso ao contexto)
   ├─ Γ₁ ⊢ 10 : Num                                       (T-Num)
   └─ sig(<) = (Num, Num) → Bool                          (assinatura)
```

Observe a semelhança com as derivações de avaliação das Aulas 8 e 12. A
árvore tem a mesma forma que teria a derivação de $\langle \texttt{let } x
= 2 + 3 \texttt{ in } x < 10, \emptyset \rangle \Downarrow 1$. A
diferença é o que há em cada nó: **tipos** em vez de valores.

#### Tentativa de derivação de um programa rejeitado

`2 + verdadeiro`:

```text
∅ ⊢ 2 + verdadeiro : ?                                    (T-Op)
├─ ∅ ⊢ 2 : Num                                            (T-Num)
├─ ∅ ⊢ verdadeiro : Bool                                  (T-Verd)
└─ sig(+) = (Bool?, …)                                    ✗
   │     sig(+) = (Num, Num) → Num, mas os operandos têm tipos (Num, Bool)
```

Não existe nenhuma outra regra que dê tipo a `2 + verdadeiro`: o programa
**não tem derivação** e é rejeitado. Repare que a rejeição não envolveu
valor algum: não calculamos `2 + 1`.

#### Um exemplo com sombreamento

`let x = 1 in let x = x < 2 in x`. O `x` interno **sombreia** o externo,
e tem outro tipo:

```text
∅ ⊢ let x = 1 in let x = x < 2 in x : Bool                (T-Let)
├─ ∅ ⊢ 1 : Num                                            (T-Num)
└─ Γ₁ ⊢ let x = x < 2 in x : Bool                         (T-Let)
   │     onde Γ₁ = ∅[x ↦ Num]
   ├─ Γ₁ ⊢ x < 2 : Bool                                   (T-Op, com x : Num)
   └─ Γ₂ ⊢ x : Bool                                       (T-Var)
      │     onde Γ₂ = Γ₁[x ↦ Bool]; Γ₂(x) = Bool
```

#### Propriedades

- **Determinismo (unicidade de tipo).** Para toda expressão `e` e todo
  contexto $\Gamma$, há **no máximo um** $\tau$ tal que $\Gamma \vdash e :
  \tau$. A forma da expressão determina a única regra aplicável (as regras
  são **dirigidas pela sintaxe**), e as premissas determinam o tipo.
- **Composicionalidade.** O tipo de uma expressão depende apenas dos tipos
  de suas subexpressões imediatas (e de $\Gamma$, para as variáveis).
- **Terminação da verificação.** Cada regra tem premissas sobre
  subexpressões **estritamente menores**. Logo, o verificador percorre a
  árvore uma única vez e **sempre termina** (neste fragmento e, como
  veremos, em `church` inteira). A verificação é muito mais barata e
  previsível que a execução.
- **Segurança de tipos.** A promessa do Bloco 3.4 ("programas bem tipados
  não dão erro de tipo") é uma propriedade que relaciona as **duas**
  semânticas (a estática e a dinâmica). Não a provaremos.


## Bloco 5: Discussão (≈ 20 min)

### 5.1 $\Gamma \vdash e : \tau$ e $\langle e, \rho \rangle \Downarrow v$: o que têm em comum?

| | Avaliação $\langle e, \rho \rangle \Downarrow v$ | Tipagem $\Gamma \vdash e : \tau$ |
|---|---|---|
| Pergunta que responde | **que valor** `e` produz? | **que tipo de valor** `e` produz? |
| Dados auxiliares | ambiente $\rho$: nomes → valores | contexto $\Gamma$: nomes → tipos |
| Notação | regras de inferência (Gentzen) | **a mesma** |
| Estrutura | dirigida pela sintaxe, **uma regra por construção** | **idem** |
| `let` | $\rho[x \mapsto v_1]$ | $\Gamma[x \mapsto \tau_1]$ |
| Escopo | léxico | **o mesmo** (por isso a mesma estrutura de (Let) e (T-Let)) |
| Resultado ausente | _stuck_ / `erro` | sem derivação (**erro de tipo**) |
| Executa o programa? | sim | **não** |
| Pode não terminar? | sim (Ω, `while 1 { }`) | **nunca** |
| Em `if` | avalia **um** dos caminhos | verifica **os dois** (Aula 21) |

O que é uma **tabela de rastreamento** de um verificador? A mesma ideia
da Aula 1, só que sobre um domínio **abstrato**: em vez de números,
calculamos tipos.

| Subexpressão | Avaliação (valor) | Verificação (tipo) |
|--------------|-------------------|--------------------|
| `2` | `2` | `Num` |
| `3` | `3` | `Num` |
| `2 + 3` | `5` | `Num` |
| `x` (com `x = 5` / `x : Num`) | `5` | `Num` |
| `x < 10` | `1` | `Bool` |

Cada linha da coluna da direita é uma **abstração** da linha
correspondente da coluna do meio: `Num` representa **todos** os números ao
mesmo tempo. É por isso que o verificador consegue prever sem executar:
ele executa o programa sobre um "mundo menor", em que há só dois valores
(`Num` e `Bool`), mais os tipos de função. Dizemos que um verificador de
tipos é uma **interpretação abstrata** do programa.

> **Curiosidade (Lógica).** Em dedução natural, $\Gamma \vdash A$ diz que a
> proposição $A$ é deduzível a partir das hipóteses em $\Gamma$. Em `church`,
> $\Gamma$ guarda hipóteses do tipo "$x$ tem tipo $\tau$". A semelhança não é
> acidental: é a **correspondência de Curry–Howard**, que mencionamos de
> passagem no plano do curso. Há um tema para uma disciplina mais avançada:
> as regras de tipo de funções são, em certo sentido, as regras da
> implicação.

### 5.2 Erros que o verificador deve reportar

Um verificador não é só um "sim ou não". Ele precisa **explicar** a
rejeição. A decisão da Aula 2 de tratar erros como **valores** (o padrão
monádico) se aplica aqui: o resultado do verificador é um `Tipo` **ou** um
`Erro`, e um erro de tipo é mais um possível **significado** de um
programa. Agora há três momentos em que um programa pode ser recusado,
antes de qualquer execução:

| Etapa | Erro | Exemplo |
|-------|------|---------|
| lexer | erro **léxico** | `2 @ 3`, `fn (x: Foo) => x` |
| parser | erro **sintático** | `fn (x) => x`, `1 < 2 < 3` |
| verificador | erro de **tipo** (semântica estática) | `2 + verdadeiro`, `x + 1` |
| interpretador | erro **dinâmico** (semântica dinâmica) | `1 / 0` |

Modelos de mensagens, para o fragmento de hoje:

| Situação | Regra | Mensagem sugerida |
|----------|-------|-------------------|
| variável sem tipo em $\Gamma$ | (T-Var) | `variável 'y' não declarada` |
| operandos não casam com a assinatura | (T-Op) | `operador '+' espera (Num, Num), mas recebeu (Num, Bool)` |
| operando de operador unário | (T-OpUn) | `operador '-' espera Num, mas recebeu Bool` |

> Uma boa mensagem diz **o que** (qual regra falhou), **onde** (qual
> subexpressão) e **por quê** (tipo esperado × tipo encontrado). Nossa
> decisão de design é **parar no primeiro erro** (o padrão monádico). Um
> compilador real tenta continuar e reportar vários, o que é bem mais
> trabalhoso (dívida técnica).

### 5.3 Linguagens reais (menção)

A decisão A, "`Bool` é um tipo próprio", não é universal:

| Linguagem | `1 + verdadeiro` (ou equivalente) | Comparações devolvem |
|-----------|----------------------------------|-----------------------|
| `church` | rejeitado (antes de executar) | `Bool` |
| Java, Rust, Haskell, OCaml | rejeitado na compilação | `boolean` / `bool` / `Bool` |
| Python | `1 + True` vale `2` (`bool` é subclasse de `int`) | `bool` |
| JavaScript | `1 + true` vale `2` (conversão implícita) | `boolean` |
| C | não há `bool` nativo em C89; comparações devolvem `int` | `int` |

Dois pontos a observar:

1. as linguagens que **mantêm** `bool` separado de número rejeitam
   `1 + true`; as que não mantêm aceitam o programa (a) do Bloco 1,
   às vezes silenciosamente. É uma decisão de design, com custos e
   benefícios (Python e JavaScript privilegiaram a flexibilidade);
2. o **apagamento de tipos** (decisão C) é o que fazem Java (para
   genéricos), OCaml, Haskell, Rust e TypeScript: depois da verificação,
   o código gerado não carrega os tipos. Já Python, que verifica tipos
   dinamicamente, carrega o tipo em cada valor.

> **Estilo de Church × estilo de Curry.** Em `church`, as anotações estão
> **escritas no programa** (`fn (x: Num) => …`): é o chamado **estilo de
> Church**, como no cálculo lambda simplesmente tipado de 1940. Em ML,
> Haskell e OCaml, os tipos são em geral **inferidos** pelo compilador a
> partir do uso (**estilo de Curry**, com o algoritmo de Hindley–Milner).
> Voltaremos a isso na Aula 22; a inferência fica fora de escopo.

### 5.4 O que um sistema de tipos custa

Tipos não são de graça: eles **rejeitam programas** (Bloco 3.4). Alguns
programas que escrevemos em `aljabr` **deixam de ser programas** de
`church`:

- a **biblioteca de booleans** da Aula 12 (`true = fn (a, b) => a`) exige
  que `a` e `b` tenham **algum** tipo. Se escrevermos `fn (a: Num, b: Num)
  => a`, a função só serve para números; para servir também a `Bool`
  seria preciso uma segunda cópia. Para ter **uma só**, seria preciso
  **polimorfismo** (*generics*, em Java), que não temos;
- o combinador $M$ (`fn (x) => x(x)`) **não admite nenhum tipo**: `x` teria
  de ser, ao mesmo tempo, `τ` e uma função que recebe `τ`, ou seja, um tipo
  infinito. Na Aula 21, com a regra de aplicação, veremos isso passo a
  passo.

Em resumo: um sistema de tipos aumenta a **segurança** e reduz a
**expressividade**. Um dos objetivos da Unidade 9 é situar essa troca no
espaço de design.

### 5.5 Alternativas (para pensar)

- E se `==` aceitasse também `Bool`? (Exercício 5.)
- E se `if` aceitasse uma condição numérica **e** uma `Bool`? (Teríamos
  de decidir o tipo da expressão `if 1 then …`; é o território de
  conversões implícitas, como em JavaScript.)
- E se o `fn` comum também aceitasse a anotação de retorno? Seria um
  mecanismo de **verificação extra** (o verificador confere que o corpo
  tem o tipo prometido).


## Bloco 6: Tabela de síntese (≈ 5 min)

Nova linha na tabela corrente (`tabela-design.md`). A coluna "Tipos" das
linhas anteriores é preenchida na Aula 21.

| Linguagem | Avaliação | Vinculação | Escopo | Abstração | Estado | Dados | Controle | Tipos |
|---|---|---|---|---|---|---|---|---|
| `aljabr` v3 | estrita, exceto `if` | `let`, `letrec` | léxico | funções recursivas | — | números + closures | `if`, recursão | dinâmicos |
| `church` | estrita, exceto `if` (a mesma de v3) | `let`, `letrec` | léxico | funções recursivas | — | números + closures (`Bool` só nos tipos) | `if` (condição `Bool`), recursão | **estáticos**; anotações obrigatórias nos parâmetros; `Bool` distinto de `Num`; apagados na execução |

Observe: `church` parte da **mesma** v3 que `aljabr` v4 e `algora`, e varia
**só** na dimensão "tipos". Esse é, mais uma vez, o argumento da Unidade 9:
as dimensões de design são **independentes**.

> Nova dimensão sugerida para a tabela: **quando** os tipos são verificados
> (dinamicamente, estaticamente) e **o que** o programador escreve
> (anotações, nada). Será necessária na Aula 22.


## Mapa para a implementação

> O verificador de referência será lido na Aula 21. Use este mapa para
> tentar implementar **o que foi especificado hoje**.

### Léxico → lexer

| Especificação | Implementação |
|---------------|---------------|
| seis novos lexemas | seis novos tipos de token: `COLON`, `TARROW`, `TNUM`, `TBOOL`, `VERDADEIRO`, `FALSO` |
| `->` antes de `-` | posição de `TARROW` na lista de regras, antes de `SUB` |
| `verdadeiro` e `falso` são reservadas | duas novas entradas no mapa de palavras reservadas |
| `Num` e `Bool` | entradas do mesmo mapa, para palavras iniciadas por maiúscula; maiúscula fora do mapa é erro léxico |

### EBNF → parser

| Regra | Função do parser |
|-------|------------------|
| `atomo` com `verdadeiro`/`falso` | em `parse_atomo`, devolve `Bool(True)` / `Bool(False)` |
| `param` | nova: `parse_param` (`NOME`, `expect(COLON)`, `parse_tipo`) |
| `params` | `parse_params` agora lê `param`s em vez de `NOME`s |
| `tipo` | nova: `parse_tipo` (decide por `TNUM`, `TBOOL` ou `LPAREN`) |
| `tipos` | nova: `parse_tipos` |
| `letrec` | após o `RPAREN`, `expect(COLON)` e `parse_tipo`, só depois o `ARROW` |

Esboço de `parse_tipo`:

```python
def parse_tipo(stream):
    """tipo ::= Num | Bool | LPAREN [ tipos ] RPAREN -> tipo"""
    if peek(TNUM):
        expect(TNUM)
        return TNum()
    if peek(TBOOL):
        expect(TBOOL)
        return TBool()
    expect(LPAREN)
    params = []
    if not peek(RPAREN):              # [ … ] vira if
        params = parse_tipos(stream)
    expect(RPAREN)
    expect(TARROW)
    ret = parse_tipo(stream)          # associatividade à direita
    return TFun(params, ret)
```

### Regras de tipo → verificador

Cada regra vira uma **cláusula** do verificador, como cada regra de
avaliação virava uma cláusula do `eval`. A assinatura é parecida com a de
`eval`: `verifica(ast, gamma) -> Tipo | Erro`.

```python
def verifica(e, gamma) -> Tipo | Erro:
    match e:
        case Num(_):                       # (T-Num)
            return TNum()
        case Bool(_):                      # (T-Verd), (T-Falso)
            return TBool()
        case Var(x):                       # (T-Var)
            if x in gamma:
                return gamma[x]
            return Erro(f"variável '{x}' não declarada")
        case Let(x, e1, e2):               # (T-Let)
            t1 = verifica(e1, gamma)
            if isinstance(t1, Erro):
                return t1
            return verifica(e2, {**gamma, x: t1})    # Γ[x ↦ τ₁], sem mutar Γ
        case BinOp(op, e1, e2):            # (T-Op)
            t1 = verifica(e1, gamma)
            if isinstance(t1, Erro):
                return t1
            t2 = verifica(e2, gamma)
            if isinstance(t2, Erro):
                return t2
            params, ret = SIG[op]          # assinatura do operador
            if (t1, t2) != params:
                return Erro(f"operador '{op}' espera {params}, mas recebeu {(t1, t2)}")
            return ret
        # (T-OpUn) é análoga; as demais regras ficam para a Aula 21
```

Pontos a observar:

- **o contexto é imutável**: `{**gamma, x: t1}` cria um **novo** contexto,
  como a "cópia estendida" do ambiente $\rho$ da Aula 8;
- a igualdade de tipos é a **estrutural** do Bloco 4.3: se `TNum`, `TBool` e
  `TFun` forem `dataclass`es, o `!=` do Python já faz o serviço;
- o verificador percorre a AST **uma vez** (terminação, Bloco 4.5);
- o `main` passa a ser: lexer → parser → verificador → (se aprovado)
  interpretador, com o padrão monádico de erros da Aula 2.

### Conjunto de testes

**Lexer e parser** (programas rejeitados e aceitos: tabelas do Bloco 4.2).

**Verificador**, com $\Gamma = \emptyset$:

| Programa | Resultado |
|----------|-----------|
| `42` | `Num` |
| `verdadeiro` | `Bool` |
| `falso` | `Bool` |
| `2 + 3 * 4` | `Num` |
| `-(2 ** 3)` | `Num` |
| `1 < 2` | `Bool` |
| `2 == 2` | `Bool` |
| `let x = 2 + 3 in x < 10` | `Bool` |
| `let x = 1 in let x = x < 2 in x` | `Bool` |
| `let a = 1 in let b = a + 1 in a * b` | `Num` |
| `let x = verdadeiro in 5` | `Num` |
| `2 + verdadeiro` | erro de tipo |
| `(1 < 2) + 1` | erro de tipo |
| `1 < verdadeiro` | erro de tipo |
| `verdadeiro == verdadeiro` | erro de tipo |
| `-verdadeiro` | erro de tipo |
| `(1 < 2) < 3` | erro de tipo |
| `x + 1` | erro de tipo (`x` não declarada) |
| `(let x = 1 in x) + x` | erro de tipo (`x` fora de escopo) |
| `let x = verdadeiro in x * 2` | erro de tipo |
| `1 / 0` | `Num` (o verificador **não** detecta divisão por zero) |

**Execução.** Todos os programas aceitos acima executam como em `aljabr`
v3, com `verdadeiro` valendo `1` e `falso` valendo `0`.


## Resumo (para guardar)

1. Em `aljabr`, erros de tipo só aparecem **durante a execução**, às vezes
   longe da origem, às vezes nunca (`2 + (1 < 2)` vale `3`). Um **sistema de
   tipos estático** detecta uma classe desses erros **antes** de executar.
2. Decisões de design de `church`: `Bool` distinto de `Num`; anotações
   obrigatórias nos parâmetros (e no retorno do `letrec`), sem inferência;
   verificação estática com **apagamento** de tipos; tipos de função
   `(τ₁, …, τₙ) -> τ`.
3. **Léxico:** seis novos tokens (`:`, `->`, `Num`, `Bool`, `verdadeiro`,
   `falso`); `->` antes de `-`. **Sintaxe:** categorias `tipo`, `tipos` e
   `param`; literais booleanos; `letrec` com tipo de retorno.
   **Semântica dinâmica:** a de v3, apenas com os literais `verdadeiro` e
   `falso`, que valem `1` e `0`.
4. **Semântica estática:** contexto $\Gamma$ (nomes → tipos), julgamento
   $\Gamma \vdash e : \tau$, assinaturas dos operadores e regras
   (T-Num), (T-Verd), (T-Falso), (T-Var), (T-Let), (T-Op) e (T-OpUn). A
   ausência de derivação é o erro de tipo.
5. $\Gamma \vdash e : \tau$ tem a mesma forma e a mesma disciplina que
   $\langle e, \rho \rangle \Downarrow v$, mas calcula **tipos** (uma
   abstração dos valores) e **sempre termina**.
6. O verificador é **conservador**: rejeita programas que executariam sem
   erro. E não detecta tudo (`1 / 0`, não terminação).


## Para a próxima aula

Hoje ficamos sem as regras das construções mais interessantes. Na **Aula 21**:

- as regras de tipo de **abstração** e **aplicação**: o que é o tipo de
  `fn (x: Num) => x + 1`? E o de `f(2)`?
- `if` (condição `Bool`; **os dois ramos com o mesmo tipo**) e `letrec` (a
  anotação de retorno e a regra que a usa);
- derivação de um exemplo com funções;
- **leitura guiada do verificador de referência**, uma função por regra,
  executado sobre programas corretos e incorretos;
- por que o verificador **não** cobre objetos, `match` nem `algora`.

Para chegar com ideias:

1. escreva o tipo de `twice` (Bloco 3.2) e tente prever que regras seriam
   necessárias para derivá-lo;
2. o que deve acontecer, no verificador, com `fn (x: Num) => x(x)`?
3. por que `if verdadeiro then 1 else 2 + verdadeiro` deveria ser rejeitado?
   (Bloco 3.4)


## Exercícios de fixação (sem necessidade de entrega)

1. **Derivações.** Derive, com as regras do Bloco 4.5, o tipo de:
   a) `let a = 2 in let b = a * a in b < 10`;
   b) `let x = 1 < 2 in 5` (o que há de curioso no tipo de `x`?).
   Para cada programa rejeitado do Bloco 3.5, aponte **qual premissa** de
   qual regra falha.

2. **Quem rejeita?** Classifique cada programa como rejeitado pelo
   **lexer**, pelo **parser**, pelo **verificador**, pelo **interpretador**
   (em tempo de execução) ou **aceito sem erro**:
   a) `fn (x) => x`
   b) `1 < 2 < 3`
   c) `(1 < 2) < 3`
   d) `10 / (5 - 5)`
   e) `let x = 3 in x + y`
   f) `Num + 1`
   g) `2 @ 3`

3. **Mais um operador.** Acrescente a `church` o operador `<=` (com a mesma
   precedência de `<` e `==`). O que muda no léxico, na EBNF, na tabela de
   assinaturas e nas **regras** de tipo? Ele precisa de uma regra nova?

4. **Apagamento.** Mostre que `let x = 5 in x < 10` tem tipo `Bool` e valor
   `1`. Que informação seria **perdida** se o `main` imprimisse apenas o valor?
   Como o tipo calculado pelo verificador a recupera?

5. **Alternativa de design.** Suponha que `==` aceitasse também dois
   `Bool`. a) Como mudaria a tabela de assinaturas? b) A regra (T-Op) da
   forma atual continua suficiente? (Dica: uma operação com **duas**
   assinaturas possíveis.) c) Que nome essa técnica tem em Java/C++? (É o
   começo de uma conversa sobre **sobrecarga** e **polimorfismo**.)

6. **Unicidade.** Dê um programa para o qual existam **dois** tipos
   derivável distintos, ou argumente por que isso não pode acontecer em
   `church` (Bloco 4.5, Determinismo).

7. **(Implementação)** Implemente `lexer`, `parser` (com `tipo`) e o
   verificador para o fragmento de hoje, a partir do mapa deste texto.
   Use os conjuntos de testes e, ao final, acrescente-os ao `main` do
   interpretador de `aljabr` v3 (com a etapa extra).

8. **(Reflexão)** Dê um programa de `church` que **executa sem erro** em
   `aljabr` v3 (sem as anotações), mas que o verificador **rejeita**.
   Defenda uma decisão de design: isso é um defeito ou o preço de ter um
   verificador estático?

---

**Leituras (opcionais)**

- CHURCH, Alonzo. *A Formulation of the Simple Theory of Types*, 1940
  (origem histórica do nome).
- PIERCE, Benjamin C. *Types and Programming Languages*, 2002. O capítulo
  sobre o cálculo lambda simplesmente tipado formaliza o que faremos nesta
  unidade.

