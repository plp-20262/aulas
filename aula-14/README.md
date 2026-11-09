# Aula 14 — 04/Nov — Unidade 4 (4/4)

> Tema da aula: `aljabr` v3 (recursão e condicional) e fechamento da
> Unidade 4: por que `aljabr` é uma linguagem **funcional pura**.
>
> - `aljabr` v3 = v2 + `letrec` + `if` + comparações (`==`, `<`)
> - início da tabela de síntese de paradigmas
> - ponte para a Unidade 5 (estado e mutação)


## Objetivo geral

Na Unidade 4 abstraímos _computações_: funções são valores (closures) e o
escopo é léxico. Hoje fechamos a unidade em três movimentos.

1. **Mostrar o limite de v2.** Com lambdas já fazemos muita coisa (alta ordem,
   `compose`, `twice`, Newton, booleans por codificação), mas não conseguimos
   escrever diretamente um fatorial. Vamos descobrir _por quê_, e cada causa
   vira uma decisão de design de v3.
2. **Especificar v3** nos três níveis de sempre: léxico (REGEX), sintaxe
   (EBNF) e semântica (regras `⟨e, ρ⟩ ⇓ v`). A implementação fica como
   tarefa, como na Aula 11.
3. **Nomear o que construímos.** Só depois de os alunos notarem as
   propriedades, nomear: funções de primeira classe e linguagem funcional
   pura. Introduzir _transparência referencial_ e ligá-la a substituição e
   ambiente. Terminar com o que ainda não conseguimos escrever, que é o gancho
   da Unidade 5.

> A "funcional" aparece como **observação**, não como rótulo anunciado. Não
> usar a expressão "programação funcional" antes do Bloco 6.


## Roteiro de tempo (≈ 2h)

| Bloco | Conteúdo                                              | Tempo  |
|-------|-------------------------------------------------------|--------|
| 1     | Retomada: escopo léxico × dinâmico                    | 8 min  |
| 2     | `aljabr` v2 em ação; funções como dados               | 15 min |
| 3     | O limite de v2: três paredes                          | 12 min |
| 4     | Decisões de design de v3                              | 15 min |
| 5     | Especificação de v3 (léxico, sintaxe, semântica)      | 25 min |
| 6     | Transparência referencial e "funcional puro"          | 15 min |
| 7     | Tabela de síntese (início)                            | 8 min  |
| 8     | O que ainda não conseguimos escrever (ponte)          | 12 min |
| 9     | Fechamento e tarefa                                   | 5 min  |

**Se o tempo apertar** (do corte menos custoso ao mais custoso):
1. derivações do Bloco 5.4 e mapa de implementação do Bloco 5.5 vão para o
   README de estudo, sem passar pela aula;
2. Bloco 2 vira só uma demonstração rápida (sem reexplicar `twice`/Newton);
3. Bloco 7 reduzido a preencher a linha de v3 e a coluna "estado".

Não cortar: Bloco 3 (motivação), as regras `(LetRec)` e `(If…)` do Bloco 5,
a definição de transparência referencial e o Bloco 8.


## Retomando da aula anterior

- Aula 11 e Aula 12: especificamos `aljabr` v2 nos três níveis. Um lambda
  avalia para um **closure** `(parâmetros, corpo, ambiente de criação)` e a
  regra (App) avalia o corpo em `ρ₀[p₁ ↦ v₁, …]`, o ambiente de **criação**.
- Aula 13: Prova 1 (Unidades 1 a 3).
- Na Aula 12, vimos programas sofisticados em v2: funções simples, funções que
  devolvem funções (multiplicador), `compose`, `twice`, os combinadores M e Ω,
  Newton para √2 e uma "biblioteca" de booleans codificados com lambdas.


## Bloco 1: Retomada — escopo léxico × dinâmico (≈ 8 min)

### 1.1 Teste rápido

Escrever no quadro e pedir resposta **antes** de rastrear:

```text
let a = 10 in
let f = fn (x) => x + a in
let a = 20 in
f(1) + a
```

- escopo léxico (o de `aljabr`): `f(1) = 1 + 10 = 11`; resultado `11 + 20 = 31`
- escopo dinâmico: `f(1) = 1 + 20 = 21`; resultado `21 + 20 = 41`

> Ver exemplos: [`escopo-lexico.py`](escopo-lexico.py) e [`escopo-dinamico.sh`](escopo-dinamico.sh).

### 1.2 A diferença de um símbolo

Reprojetar as regras (App) e (AppDin) da Aula 12 §7.1: a única diferença é o
ambiente em que o corpo é avaliado, `ρ₀` (criação) ou `ρ` (chamada).

> **Pergunta:** no escopo dinâmico, o que decide o valor de `f(1)`?
>
> Resposta: **quem chamou** e **quando**. O significado de `f` deixa de ser
> propriedade de `f`. Guarde essa ideia: ela volta no Bloco 6.

Ponto a registrar: no escopo léxico, o significado de uma função fica fixado
no momento em que ela é criada. É o que torna segura a captura do ambiente.


## Bloco 2: `aljabr` v2 em ação (≈ 15 min)

> Reaproveitar o código mostrado na Aula 12. Os programas abaixo são só um
> lembrete do que cabe no quadro.

### 2.1 O que já escrevemos

```text
# função que devolve função (closures criados em tempo de execução)
let faz_multiplicador = fn (n) => fn (x) => n * x in
let dobro  = faz_multiplicador(2) in
let triplo = faz_multiplicador(3) in
dobro(21) + triplo(1)                       # 45

# função que recebe função
let compose = fn (f, g) => fn (x) => f(g(x)) in
let twice   = fn (f) => fn (x) => f(f(x)) in
twice(twice(dobro))(1)                      # 16

# a biblioteca de booleans
let true   = fn (a, b) => a in
let false  = fn (a, b) => b in
let not    = fn (p) => p(false, true) in
let and    = fn (p, q) => p(q, false) in
let to_num = fn (p) => p(1, 0) in
to_num(and(true, not(false)))               # 1
```

Mais: Newton para √2 com `twice`, e o par M/Ω (`M = fn (x) => x(x)`;
`Ω = M(M)` não termina).

### 2.2 Deixar a turma notar (sem nomear ainda)

Perguntas, uma por vez:

1. Em quais pontos desses programas uma função foi **passada como argumento**?
   Foi **devolvida** por outra função? Foi **guardada em um nome**?
2. `dobro` e `triplo` têm o mesmo código (`fn (x) => n * x`). O que os torna
   funções diferentes?
   - Resposta: cada uma é um closure distinto, **criado em tempo de execução**,
     com seu próprio `ρ₀` (`n ↦ 2` e `n ↦ 3`).
3. Na biblioteca de booleans, o que é `true`? Que tipo de "coisa" ele é?
   - Resposta: uma função. Um **dado** (verdadeiro) codificado como função.

### 2.3 Nomear: funções de primeira classe

Só agora definir:

> Um valor é de **primeira classe** quando pode ser (1) nomeado por uma
> variável, (2) passado como argumento, (3) devolvido como resultado e (4)
> criado em tempo de execução, exatamente como qualquer outro valor da
> linguagem.

Evidência formal, já presente na especificação: $\mathrm{Val} = ℝ ∪
\mathrm{Clo} ∪ \\{\mathtt{erro}\\}$. Closures moram no **mesmo conjunto** que
os números: são dados em tempo de execução.

Observações:

- (5) "armazenar em estruturas de dados" não se aplica ainda: `aljabr` não tem
  estruturas (virão na Unidade 7).
- Contraste com linguagens que conhecem: em C, ponteiros para função apontam
  para código definido em tempo de compilação, sem closures; em Java, lambdas
  chegaram só no Java 8; em Python, `def` e `lambda` já criam closures.
- Gancho para frente (apenas plantar): em Java, a variável local capturada por
  um lambda precisa ser _final_ ou _efetivamente final_. **Por quê?** Fica
  como pergunta aberta para a Unidade 5.


## Bloco 3: O limite de v2 — três paredes (≈ 12 min)

### 3.1 O desafio

**Pergunta à turma:** escreva `fatorial` em nossa linguagem `aljabr` (v2).

<details>
<summary>Clique pra ver a resposta</summary>
   
```text
let fat = fn (n) => se(n == 0, 1, n * fat(n - 1)) in
fat(3)
```

O problema dessa solução é que ela esbarra em **três paredes**. Cada uma vira uma decisão do Bloco 4.
</details>

### 3.2 Parede 1: o nome `fat` não existe dentro do corpo

```text
let f = fn (n) => f(n) in f(1)          # erro: f não vinculada
```

Pela regra (Let), `e₁` é avaliada em `ρ`, **antes** de `f` ser vinculada.
O closure é criado com `ρ₀ = ρ`, no qual `f` não existe. Quando o corpo roda e
procura `f` em `ρ₀[n ↦ 1]`, o ambiente (lifted) devolve `erro`.

Voltar à observação da Aula 12 §4.1: closures são construídos "de dentro para
fora". Para o closure de `f` conter `f`, precisamos de algo que ainda não
temos.

### 3.3 Parede 2: avaliação estrita de `se` (escolha falsa de caminhos)

Por um momento, assuma que `f` estivesse visível dentro do corpo, olhe como a
função de seleção `se` (nosso `if`) é definida em a nossa biblioteca:

```text
let se = fn (cond, then, else) => cond(then, else) in
let a = 0 in
se(true, 1 * a, 1 / a)                        # erro!
```

Observe que `se(true, 1*a, 1/a)` deveria valer `1`, mas vale `erro`. O problema é que
a regra (App) estabelece o que se chama de _ordem aplicativa de avaliação_ em que
**todos os argumentos são avaliados antes do corpo** (e erros são estritos). Com isso,
em `fat`, o caminho `n * fat(n - 1)` seria avaliado até mesmo quando `n == 0`, o que
geraria chamadas a `fat(-1)`, `fat(-2)`, … e a computação não terminaria.

> **Pergunta:** observe que o `and` de nossa "biblioteca" avalia os dois argumentos
> sempre. E o `and` de Python? E o `&&` de Java?
> <details>
> <summary>Clique pra ver a resposta</summary>
>
> <br>Resposta: o `and` de Python e o `&&` não avaliam o segundo operando se o primeiro
> for falso. É o que chamamos de avaliação _preguiçosa_ da expressão. Nessas linguagens,
> o `and` e o `&&` **não** são funções comuns: são uma _forma especial_ da linguagem com uma
> regra semântica própria.
> </details>

Moral: o problema não são os booleans (nativos ou codificados). É a
**estratégia de avaliação** da aplicação de função: a chamada avaliação estrita (ou ordem
aplicativa de avaliação).

### 3.4 Parede 3: não há como testar um número

Para escolher um caminho precisamos de uma **condição**, mas v2 não tem
comparação alguma. Números entram, números saem; mas nenhum caminho leva de
`n` até `true`/`false`. Não existe nem temos como implementar `eh_zero(n)`
em v2.

> Veja que com nossa biblioteca de booleans, nosso problema não é a falta de
> booleans nativos na linguagem. É que não temos como produzir booleans a partir
> de condições sobre os números. 


### 3.5 Resumo dessas "paredes"

| Parede | Sintoma                                          | Causa                                          | Decisão (Bloco 4) |
|--------|--------------------------------------------------|------------------------------------------------|-------------------|
| 1      | função não enxerga a si própria                  | nosso `let` não é recursivo                    | **C**             |
| 2      | os dois caminhos do `se` são sempre avaliados    | aplicação de função é _avaliação estrita_      | **B**             |
| 3      | não há como decidir com base num número          | não há operadores de comparação                | **A**             |

> **Nota (de honestidade intelectual).** _Strictly speaking_,
> recursão **é**, sim, possível em v2: o par de combinadores M/Ω que mostrei na
> aula passada é um exemplo de auto-aplicação.
> O combinador **Z** (o equivalente ao combinador Y para avaliação estrita) permite fazer
> recursão sem nome. A
> condicional também pode ser simulada com _thunks_ (ver Bloco 4, decisão B).
> Então o que v2 não permite é recursão **direta, legível e com condição
> preguiçosa**. Convém dizer, portanto, que "não conseguimos escrever _diretamente_".
> De fato, algum de vocês pode ter percebido que o combinador M é uma _auto-aplicação_.
> 

## Bloco 4: Decisões de design de v3 (≈ 15 min)

Mesmo formato da Aula 09: critérios, alternativas, decisão registrada. As
colunas "decisão-alvo" indicam o resultado que o roteiro assume (a turma pode
chegar a outro; ver ajustes ao final de cada decisão).

### 4.1 Decisão A — como expressar uma condição

| # | Opção                                                     | Domínio novo? | Comparações devolvem | Consequências                                                                                  |
|---|-----------------------------------------------------------|---------------|----------------------|------------------------------------------------------------------------------------------------|
| 1 | booleans nativos (`true`/`false` como literais)           | sim (`Bool`)  | `Bool`               | mais regras de erro (`1 + true`); conflita com os nomes `true`/`false` da biblioteca           |
| 2 | **condição numérica**: `0` é falso, qualquer outro é verdadeiro | não    | `1` ou `0`           | menor mudança; `2 + (1 < 2)` passa a valer `3`; é o estilo de C                                |

**Decisão-alvo: opção 2.**

- Operadores novos: `==` e `<` (os demais, `<=`, `>`, `>=`, `!=`, ficam como
  exercício: derivam-se com `if`).
- Comparações aplicadas a closures dão `erro` (pelo _lift_).
- Consequência deliberada para a Unidade 8: com a opção 2, `2 + (1 < 2)` não é
  erro. É um bom motivo para os **tipos estáticos** (booleans como tipo
  distinto), e não um defeito a esconder. Anotar isso na tabela de síntese.
- Ponte com a biblioteca de booleans: `to_num` já converte os nossos booleans
  codificados em `1`/`0`, então `if to_num(and(true, not(false))) then 10 else
  20` funciona.

> Se a turma preferir a opção 1: acrescentar `Bool` a `Val`, literais
> `true`/`false` como palavras reservadas (e renomear a biblioteca), e uma
> regra de erro para `if` com condição que não seja booleana.

### 4.2 Decisão B — como escolher entre dois caminhos

| # | Opção                                                      | Funciona sob avaliação estrita? | Observação                                                              |
|---|------------------------------------------------------------|---------------------------------|-------------------------------------------------------------------------|
| 1 | função comum `se(c, a, b)`                                 | ❌ (parede 2)                    | em Haskell funcionaria: avaliação não estrita                           |
| 2 | função + _thunks_: `se(c, fn () => a, fn () => b)()`       | ✅                               | verboso, e o programador precisa lembrar de embrulhar; é a ideia de `ifTrue:ifFalse:` em Smalltalk |
| 3 | **forma especial** `if c then a else b`, que só avalia um caminho | ✅                           | exige nova sintaxe e nova regra; é a escolha de Scheme, Python (`a if c else b`), C (`?:`) |

**Decisão-alvo: opção 3**, com `else` **obrigatório**. Razão: `if` é uma
_expressão_ (todo `if` produz um valor), logo precisa dos dois caminhos.

Demonstrar a opção 2 rapidamente (ela é a prova de que a estrita não impede
simulação):

```text
let se = fn (c, t, e) => c(t, e)() in
se(true, fn () => 1, fn () => 1/0)      # 1
```

> **Pergunta:** a opção 3 trata os caminhos de forma diferente da aplicação de
> função. Em que ponto da _regra_ vamos enxergar isso?
> <details>
> <summary>Clique pra ver a resposta</summary>
>
> <br>Resposta: nas premissas. Em (App) e (Op), **todas** as subexpressões
> aparecem como premissa. Na regra de `if`, só **um** dos caminhos aparece.
> A forma da regra _é_ a estratégia de avaliação.
> </details>

Lembrete de gramática (Aula 06): em `S ::= if E then S [ else S ]` o `else`
pendente dava ambiguidade. Aqui, como `if` é expressão e `else` é obrigatório,
**o problema desaparece**.

### 4.3 Decisão C — como permitir que uma função se chame

| # | Opção                                           | `let` mantém o significado de v1/v2? | Exemplo-teste: `let x = 1 in let x = x + 1 in x` | Observação                                                       |
|---|-------------------------------------------------|--------------------------------------|---------------------------------------------------|------------------------------------------------------------------|
| 1 | tornar o `let` sempre recursivo                 | ❌ muda                               | `x` passa a depender de si mesmo (mal definido)   | é o que faz Haskell (com avaliação preguiçosa)                   |
| 2 | **nova construção** `letrec`, só para lambdas   | ✅ inalterado                         | continua valendo `2`                              | Scheme `letrec`, OCaml `let rec`                                 |
| 3 | combinador de ponto fixo (Z), sem mudar a linguagem | ✅                                | ✅                                                | correto, mas ilegível; é o lambda cálculo puro                   |

**Decisão adotada: opção 2**, com `letrec` restrito sintaticamente a lambdas.

- Restringir a lambda evita `letrec x = x + 1 in x` (mal definido) sem
  precisar de regra de erro especial.
- A restrição é **sintática**: o parser rejeita `letrec x = 5 in x`.
- Limitação assumida: `letrec` define **uma** função por vez; não há recursão
  mútua.

> **Pergunta:** o que deveria valer `let x = 1 in let x = x + 1 in x` se `let`
> fosse recursivo?
> <details>
> <summary>Clique pra ver a resposta</summary>
>
> <br>Resposta: não há resposta boa. O idioma de _re-vincular_ um nome ao
> próprio valor anterior deixaria de funcionar. Por isso `letrec` é uma
> construção à parte.
> </details>

Na prática: Python e JavaScript permitem recursão em `def`/`function` porque o
corpo procura o nome no escopo envolvente **na hora da chamada**; em Java, um
lambda atribuído a uma variável local não pode se referir à própria variável.

### 4.4 Registro

```text
Decisão da turma (A): condição numérica (0 é falso; comparações devolvem 1 ou 0)
Decisão da turma (B): `if` como forma especial, com `else` obrigatório
Decisão da turma (C): `letrec`, restrito a lambdas
Dívidas técnicas: recursão mútua; booleans distintos de números (Unidade 8)
```


## Bloco 5: Especificação de `aljabr` v3 (≈ 25 min)

### 5.1 Léxico

Quatro novas palavras reservadas e dois novos operadores (as palavras
reservadas passam a ser sete).

```text
LETREC  ::=  letrec           ← NOVO (palavra reservada)
IF      ::=  if               ← NOVO (palavra reservada)
THEN    ::=  then             ← NOVO (palavra reservada)
ELSE    ::=  else             ← NOVO (palavra reservada)
EQEQ    ::=  ==               ← NOVO
LT      ::=  <                ← NOVO
```

Palavras reservadas: `let`, `in`, `fn`, `letrec`, `if`, `then`, `else`.

> **Pergunta (ordem das regras, de novo):** quais pares de tokens
> compartilham prefixo agora? Em que ordem devem ser tentados?
> <details>
> <summary>Clique pra ver a resposta</summary>
>
> <br>Resposta: `==` e `=>` precisam ser tentados **antes** de `=`. E
> `letrec` deve ser reconhecido como um lexema completo antes de `let` (ou,
> melhor: o lexer casa `NOME` e **depois** consulta o mapa de reservadas, de
> modo que `letrec` nunca vira `let` + `rec`).
> </details>

### 5.2 Sintaxe concreta (EBNF)

Mesma observação de notação da Aula 11: os parênteses da _linguagem_ são
`LPAREN`/`RPAREN`; os parênteses `( … )` da EBNF são meta-símbolos.

```text
exp     ::= let NOME = exp in exp
          | letrec NOME = fn LPAREN [ params ] RPAREN => exp in exp      ← NOVO
          | fn LPAREN [ params ] RPAREN => exp
          | if exp then exp else exp                                    ← NOVO
          | comp
comp    ::= soma [ ( == | < ) soma ]                                    ← NOVO
soma    ::= termo { ( + | - ) termo }          (antes, parte de exp)
termo   ::= fator { ( * | / ) fator }
fator   ::= unario [ ** fator ]
unario  ::= [ + | - ] chamada
chamada ::= atomo { LPAREN [ args ] RPAREN }
atomo   ::= INTEIRO | NOME | LPAREN exp RPAREN
params  ::= NOME { , NOME }
args    ::= exp { , exp }
```

Mudanças em relação à v2:
1. `exp` ganhou `letrec` e `if`;
2. nasceu o nível `comp` entre `exp` e `soma`;
3. o corpo que antes era de `exp` (`termo { (+|-) termo }`) passou a se chamar
   `soma`.

A gramática continua LL(1): `LETREC`, `IF`, `FN` e `LET` decidem a alternativa
de `exp`; `==` ou `<` decidem se `comp` tem o lado direito opcional.

**Decisões de design codificadas na gramática** (mesma disciplina da Aula 05):

- **Precedência** (da menor para a maior):

  | Nível | Construções                                                   |
  |-------|---------------------------------------------------------------|
  | 1     | `let`, `letrec`, `fn`, `if` (o corpo se estende à direita)    |
  | 2     | `==` `<`                                                      |
  | 3     | `+` `-` (binários)                                            |
  | 4     | `*` `/`                                                       |
  | 5     | `**`                                                          |
  | 6     | `+` `-` (unários)                                             |
  | 7     | aplicação `f(…)`, parênteses                                  |

  Assim, `n - 1 == 0` é `(n - 1) == 0`.

- **Associatividade de `==` e `<`: nenhuma.** O `[ … ]` (e não `{ … }`) na regra
  `comp` rejeita `1 < 2 < 3`. É uma decisão: Python aceita (encadeia), C
  aceita e associa à esquerda; nós optamos por rejeitar.

- **`if` e `letrec` só como operandos entre parênteses**, como `fn` e `let`:
  `1 + if …` é erro sintático; `1 + (if …)` é válido. O `else` se estende o
  máximo possível: `if c then a else b + 1` tem `b + 1` como caminho.

Programas que o parser deve **rejeitar**:

| Programa                               | Por quê                                         |
|----------------------------------------|-------------------------------------------------|
| `1 < 2 < 3`                            | `comp` não é associativa                        |
| `if x then 1`                          | `else` obrigatório                              |
| `letrec x = 5 in x`                    | o lado direito de `letrec` precisa ser `fn`     |
| `1 + if 1 then 2 else 3`               | `if` como operando sem parênteses               |
| `let if = 1 in if`                     | `if` é palavra reservada                        |

### 5.3 Sintaxe abstrata e semântica

Novos nós de AST (parênteses, `then`, `else` e vírgulas não aparecem):

```text
If(cond, então, senão)
LetRec(nome, Lambda(params, corpo_fn), corpo)
```

`==` e `<` são operadores binários comuns (`Eq`, `Lt`); a regra (Op) da Aula 12
apenas passa a admitir `op ∈ {+, -, *, /, **, ==, <}`.

> **Nota de implementação** (retomando a questão da Aula 12 §6.2): com `If`,
> `LetRec`, `Let`, `Lambda` e `App`, todos com 2 a 4 componentes, uma AST feita
> de listas fica ambígua. É um bom momento para migrar a AST para
> `dataclass`es, que vamos precisar na Unidade 7 de qualquer jeito.

**Domínios semânticos: nenhuma mudança.** $\mathrm{Val} = ℝ ∪ \mathrm{Clo} ∪
\\{\mathtt{erro}\\}$ (decisão A, opção 2). As comparações são operações
semânticas $f_{==}, f_{<} : ℝ \times ℝ \to \\{0, 1\\}$ e, como as demais, são
levadas a $\mathrm{Val}$ pelo _lift_ (closures em comparações dão `erro`).

**Condicional.** Observe que só **um** caminho aparece nas premissas:

$$
\frac{
  \langle c, \rho \rangle \Downarrow n \quad (n \in ℝ,\ n \neq 0) \qquad
  \langle e_1, \rho \rangle \Downarrow v
}{
  \langle \texttt{if}\ c\ \texttt{then}\ e_1\ \texttt{else}\ e_2,\ \rho \rangle \Downarrow v
} \quad \text{(IfVerd)}
$$

$$
\frac{
  \langle c, \rho \rangle \Downarrow 0 \qquad
  \langle e_2, \rho \rangle \Downarrow v
}{
  \langle \texttt{if}\ c\ \texttt{then}\ e_1\ \texttt{else}\ e_2,\ \rho \rangle \Downarrow v
} \quad \text{(IfFalso)}
$$

$$
\frac{
  \langle c, \rho \rangle \Downarrow v_c \qquad v_c \in \mathrm{Clo}
}{
  \langle \texttt{if}\ c\ \texttt{then}\ e_1\ \texttt{else}\ e_2,\ \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(IfCond)}
$$

Se a condição avalia para `erro`, vale a convenção de propagação da Aula 12
§4.2. O caminho não escolhido **nunca é avaliado**, logo seus erros e sua
não-terminação nunca acontecem.

**Recursão.** A regra define um ambiente em termos de si mesmo:

$$
\frac{
  \rho_1 = \rho[f \mapsto \mathsf{clo}((p_1, \ldots, p_n),\ e_f,\ \rho_1)]
  \qquad
  \langle e_2, \rho_1 \rangle \Downarrow v
}{
  \langle \texttt{letrec}\ f = \texttt{fn}\ (p_1, \ldots, p_n) \Rightarrow e_f\ \texttt{in}\ e_2,\ \rho \rangle \Downarrow v
} \quad \text{(LetRec)}
$$

Leitura: a primeira premissa não é uma avaliação, é uma **equação** que
descreve $\rho_1$. Ele é o ambiente em que $f$ já existe e é o closure de $f$
cujo ambiente de criação é... o próprio $\rho_1$. Logo, quando o corpo de $f$
procura $f$, encontra.

> **Volta da observação da Aula 12 §4.1.** Lá dissemos que closures são
> construídos "de dentro para fora" e que isso voltaria com a recursão. Aqui
> o ciclo é **genuíno**: o ambiente contém o closure, que contém o ambiente.
> (Tecnicamente, $\rho_1$ é um ponto fixo; não precisamos desse formalismo.)
>
> Nenhuma outra regra muda. Em particular, (App) continua avaliando o corpo
> em $\rho_0[\ldots]$: é o fato de $\rho_0 = \rho_1$ conter $f$ que faz a
> recursão funcionar.

### 5.4 Derivação de exemplo

`letrec fat = fn (n) => if n == 0 then 1 else n * fat(n - 1) in fat(2)`

```text
⟨letrec fat = … in fat(2), ∅⟩ ⇓ 2                                   (LetRec)
│     onde ρ' = ∅[fat ↦ C]   e   C = clo((n), if n == 0 then 1 else n * fat(n - 1), ρ')
└─ ⟨fat(2), ρ'⟩ ⇓ 2                                                (App)
   ├─ ⟨fat, ρ'⟩ ⇓ C                                                (Var)
   ├─ ⟨2, ρ'⟩ ⇓ 2                                                  (Num)
   └─ ⟨if n == 0 then 1 else n * fat(n - 1), ρ'[n ↦ 2]⟩ ⇓ 2        (IfFalso)
      ├─ ⟨n == 0, ρ'[n ↦ 2]⟩ ⇓ 0                                   (Op)
      └─ ⟨n * fat(n - 1), ρ'[n ↦ 2]⟩ ⇓ 2                          (Op)
         ├─ ⟨n, ρ'[n ↦ 2]⟩ ⇓ 2                                     (Var)
         ├─ ⟨fat(n - 1), ρ'[n ↦ 2]⟩ ⇓ 1                            (App)
         │  ├─ ⟨fat, ρ'[n ↦ 2]⟩ ⇓ C      ← achou `fat` porque ρ' a contém
         │  ├─ ⟨n - 1, ρ'[n ↦ 2]⟩ ⇓ 1                              (Op)
         │  └─ ⟨if …, ρ'[n ↦ 1]⟩ ⇓ 1                               (IfFalso)
         │     └─ ⋯ análoga, com n * fat(0) = 1 * 1
         └─ *↑(2, 1) = 2
```

E o caso-base (o caminho **não** escolhido nunca aparece):

```text
⟨if 1 then 5 else 1/0, ∅⟩ ⇓ 5                                      (IfVerd)
├─ ⟨1, ∅⟩ ⇓ 1                                                      (Num)
└─ ⟨5, ∅⟩ ⇓ 5                                                      (Num)
```

Contraste com `se(true, 1 * a, 1 / a)` (Bloco 3.3): lá, `1 / a` é premissa de
(App) e produz `erro`. Aqui, o caminho não escolhido não é premissa de nada.

### 5.5 Mapa para a implementação (tarefa)

| Especificação                              | Implementação                                                                                   |
|--------------------------------------------|-------------------------------------------------------------------------------------------------|
| 6 novos lexemas                            | seis novos tipos de token (`LETREC`, `IF`, `THEN`, `ELSE`, `EQEQ`, `LT`); `==` e `=>` antes de `=` |
| `exp` com `if`/`letrec`; `comp`; `soma`    | `parse_exp` decide por `IF`/`LETREC`; novas funções `parse_comp` e `parse_soma`                  |
| `letrec` só com `fn`                       | após `=`, `expect(FN)`; qualquer outra coisa é erro sintático                                   |
| (IfVerd), (IfFalso), (IfCond)              | `eval` avalia **só** a condição, e depois **só um** dos caminhos (não reaproveitar o caminho de `Op`) |
| (LetRec)                                   | criar o closure cujo ambiente de criação **já contém** o próprio closure                        |

Conjunto de testes:

| Programa                                                                                    | Resultado     |
|---------------------------------------------------------------------------------------------|---------------|
| `letrec fat = fn (n) => if n == 0 then 1 else n * fat(n - 1) in fat(5)`                    | `120`         |
| `letrec fib = fn (n) => if n < 2 then n else fib(n - 1) + fib(n - 2) in fib(10)`            | `55`          |
| `letrec soma = fn (n) => if n == 0 then 0 else n + soma(n - 1) in soma(100)`                | `5050`        |
| `let n = 5 in letrec f = fn (x) => if x == 0 then n else f(x - 1) in f(3)`                  | `5`           |
| `if 1 then 5 else 1/0`                                                                      | `5`           |
| `if 0 then 1/0 else 7`                                                                      | `7`           |
| `if to_num(and(true, not(false))) then 10 else 20` (com a biblioteca de booleans)           | `10`          |
| `2 == 2`  /  `1 < 0`                                                                        | `1`  /  `0`   |
| `letrec f = fn (n) => f(n) in 5`                                                            | `5`           |
| `let f = fn (n) => f(n) in f(1)`                                                            | `erro`        |
| `if (fn (x) => x) then 1 else 2`                                                            | `erro`        |
| `(fn (x) => x) == 1`                                                                        | `erro`        |
| `let x = 1 in let x = x + 1 in x`                                                           | `2`           |

> Para quem tiver curiosidade: a recursão profunda em aljabr consome a pilha de
> Python, e `fat(5000)` pode levantar `RecursionError`. Mas veja que isso é uma limitação do
> interpretador, não da linguagem objeto: as regras de avaliação não dizem nada sobre pilha.
> Scheme e outras LPs funcionais vão além e exigem que chamadas em posição final não consumam
> pilha; o GHC aloca a pilha no heap, e por isso recursões fundas costumam funcionar em
> Haskell. Em Python, dá para obter algo parecido reescrevendo o eval com um trampolim
> ou uma pilha explícita, mas isso muda o interpretador, não a linguagem.
