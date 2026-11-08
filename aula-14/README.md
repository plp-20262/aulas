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

**Decisão-alvo: opção 2**, com `letrec` restrito sintaticamente a lambdas.

- Restringir a lambda evita `letrec x = x + 1 in x` (mal definido) sem
  precisar de regra de erro especial.
- A restrição é **sintática**: o parser rejeita `letrec x = 5 in x`.
- Limitação assumida (ficar registrada): `letrec` define **uma** função por
  vez; não há recursão mútua.

> **Pergunta (para provocar):** o que deveria valer `let x = 1 in let x = x +
> 1 in x` se `let` fosse recursivo?
>
> Resposta: não há resposta boa. O idioma de _re-vincular_ um nome ao próprio
> valor anterior deixaria de funcionar. Por isso `letrec` é uma construção à
> parte.

Real: Python e JavaScript permitem recursão em `def`/`function` porque o corpo
procura o nome no escopo envolvente **na hora da chamada**; em Java, um lambda
atribuído a uma variável local não pode se referir à própria variável.

### 4.4 Registro

```text
Decisão da turma (A): <condição numérica / booleans nativos>
Decisão da turma (B): <forma especial `if`>
Decisão da turma (C): <letrec restrito a lambdas>
Dívidas técnicas: recursão mútua; booleans distintos de números (Unidade 8)
```


## Bloco 5: Especificação de `aljabr` v3 (≈ 25 min)

### 5.1 Léxico

Cinco novos lexemas para palavras e dois operadores (as palavras reservadas
passam a ser sete).

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
>
> Resposta: `==` e `=>` precisam ser tentados **antes** de `=`. E `letrec`
> deve ser reconhecido como um lexema completo antes de `let` (ou, melhor: o
> lexer casa `NOME` e **depois** consulta o mapa de reservadas, de modo que
> `letrec` nunca vira `let` + `rec`).

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

> **Questão de projeto (retomando a da Aula 12 §6.2):** com `If`, `LetRec`,
> `Let`, `Lambda` e `App` todos com 2 a 4 componentes, listas ficam
> ambíguas. É um bom momento para migrar a AST para `dataclass`es (que vamos
> precisar na Unidade 7 de qualquer jeito).

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
  \rho' = \rho[f \mapsto \mathsf{clo}((p_1, \ldots, p_n),\ e_f,\ \rho')]
  \qquad
  \langle e_2, \rho' \rangle \Downarrow v
}{
  \langle \texttt{letrec}\ f = \texttt{fn}\ (p_1, \ldots, p_n) \Rightarrow e_f\ \texttt{in}\ e_2,\ \rho \rangle \Downarrow v
} \quad \text{(LetRec)}
$$

Leitura: a primeira premissa não é uma avaliação, é uma **equação** que
descreve $\rho'$. Ele é o ambiente em que $f$ já existe e é o closure de $f$
cujo ambiente de criação é... o próprio $\rho'$. Logo, quando o corpo de $f$
procura $f$, encontra.

> **Volta da observação da Aula 12 §4.1.** Lá dissemos que closures são
> construídos "de dentro para fora" e que isso voltaria com a recursão. Aqui
> o ciclo é **genuíno**: o ambiente contém o closure, que contém o ambiente.
> (Tecnicamente, $\rho'$ é um ponto fixo; não precisamos desse formalismo.)
>
> Nenhuma outra regra muda. Em particular, (App) continua avaliando o corpo
> em $\rho_0[\ldots]$: é o fato de $\rho_0 = \rho'$ conter $f$ que faz a
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

Contraste com `se(true, 5, 1/0)` (Bloco 3.3): lá, `1/0` é premissa de (App) e
produz `erro`. Aqui, não é premissa de nada.

### 5.5 Mapa para a implementação (tarefa)

| Especificação                              | Implementação                                                                                   |
|--------------------------------------------|-------------------------------------------------------------------------------------------------|
| 6 novos lexemas                            | três tokens (`EQEQ`, `LT` e as palavras reservadas); `==` e `=>` antes de `=`                   |
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

Observação para quem tiver curiosidade: a recursão profunda em `aljabr`
consome pilha de **Python**. Scheme garante chamadas finais sem crescimento de
pilha; Python não.


## Bloco 6: Transparência referencial e linguagem funcional pura (≈ 15 min)

### 6.1 Transparência referencial

Definir no quadro:

> Uma expressão é **referencialmente transparente** quando pode ser
> **substituída pelo seu valor** em qualquer ponto do programa sem alterar o
> significado do programa.

Apoiar na álgebra (nome do `aljabr` e matéria do ensino médio): se `x = 2 + 3`,
então `x * x`, `5 * 5` e `(2 + 3) * (2 + 3)` são intercambiáveis. Em
`aljabr`:

```text
let x = 2 + 3 in x * x          # 25
# ≡ 5 * 5
# ≡ (2 + 3) * (2 + 3)
```

E com funções:

```text
let dobro = fn (x) => 2 * x in
dobro(21) + dobro(21)           # ≡ 42 + 42 ≡ 2 * dobro(21)
```

Consequências (listar):

1. avaliar a mesma expressão duas vezes **sempre** dá o mesmo valor;
2. o valor de uma expressão depende **só** das subexpressões e do ambiente
   (isso é exatamente o **determinismo** + a **composicionalidade** que
   registramos nas Aulas 7, 8 e 12);
3. a ordem de avaliação de subexpressões independentes não altera o valor.
   (Ressalva fina: erro e não-terminação podem competir; não vamos explorá-la.)
4. podemos raciocinar **equacionalmente**: substituir iguais por iguais.

> **Efeito colateral:** qualquer coisa observável de uma computação além do
> valor que ela produz. `aljabr` não tem nenhum: executar um programa só
> produz o seu valor.

### 6.2 Elo com substituição e ambiente

Na Aula 8, os dois modelos de `let` foram apresentados lado a lado:

- **por substituição:** `let x = 10 in (x - 1) * (x + 1)` vira `(10 - 1) * (10 +
  1)`;
- **por ambiente:** mantemos `ρ = {x ↦ 10}` e consultamos quando preciso.

> **Pergunta:** por que dois modelos tão diferentes dão o **mesmo** resultado
> em `aljabr`?
>
> Resposta: porque a linguagem é referencialmente transparente. Substituir um
> nome pelo seu valor é seguro justamente porque o valor nunca "muda por
> baixo". O modelo de ambiente é só a versão implementável do modelo de
> substituição (e evita o cuidado extra com captura de variáveis, que o
> closure resolve de graça).

Ligar com o Bloco 1: no escopo dinâmico, o significado de `f` depende do
contexto de chamada. Escopo dinâmico **ameaça** a transparência referencial;
escopo léxico a preserva.

> **Frase para guardar (e retomar na Aula 15):** o modelo de substituição só
> vale enquanto avaliar uma expressão não deixa efeito. Se algo puder mudar, o
> "valor de `x`" depende de **quando** perguntamos.

### 6.3 Nomear: linguagem funcional pura

Perguntar: **o que `aljabr` v3 tem? E o que não tem?** Montar a tabela com a
turma:

| O que **introduzimos**                                  | O que **não** introduzimos                  |
|---------------------------------------------------------|---------------------------------------------|
| expressões (tudo produz valor, inclusive `if`)          | atribuição (`x := v`)                       |
| funções como valores (primeira classe)                  | mutação de qualquer valor                   |
| closures e escopo léxico                                | sequenciamento de comandos                  |
| recursão como único mecanismo de repetição              | laços (`while`, `for`)                      |
| transparência referencial                               | estado que muda ao longo do tempo           |
|                                                         | efeitos colaterais                          |

Só então nomear:

> `aljabr` é uma linguagem **funcional pura**. "Funcional" porque funções são
> valores e a computação é aplicação de funções; "pura" porque **não há
> efeitos**. O nome descreve um **conjunto de escolhas de design** e,
> principalmente, **o que abrimos mão**: a mutação.

Fechos adicionais:

- (com `letrec`, `if` e aritmética, `aljabr` v3 é **Turing-completa**; e com
  sintaxe infixa é, na prática, o lambda cálculo.)
- "Funcional" não é propriedade de uma linguagem específica. Python, Java e
  JavaScript permitem **programar** em estilo funcional se o programador
  _escolher não usar_ certas features. Retomaremos isso na síntese
  (Unidade 9).


## Bloco 7: Tabela de síntese (início) (≈ 8 min)

Apresentar o arquivo `tabela-design.md`. Linhas: linguagens-objeto; colunas:
dimensões de design. Preencher **com os alunos** as linhas até aqui. Marcar
explicitamente "ainda não temos" nas colunas que não existem.

| Linguagem   | Avaliação                  | Vinculação        | Escopo                     | Abstração           | Estado | Dados                          | Controle                      | Tipos   |
|-------------|----------------------------|-------------------|----------------------------|---------------------|--------|--------------------------------|-------------------------------|---------|
| `rpn`       | pilha, estrita             | —                 | —                          | —                   | —      | números                        | sequência de tokens           | dinâmicos |
| `mlisp`     | recursiva sobre a AST      | —                 | —                          | —                   | —      | números                        | composição de expressões      | dinâmicos |
| `calc`      | recursiva sobre a AST      | —                 | —                          | —                   | —      | números                        | composição de expressões      | dinâmicos |
| `aljabr` v1 | por ambiente, estrita      | `let` (não rec.)  | léxico                     | valores nomeados    | —      | números                        | —                             | dinâmicos |
| `aljabr` v2 | por ambiente, estrita      | `let` (não rec.)  | léxico (closure)           | **computações**     | —      | números + closures             | —                             | dinâmicos |
| `aljabr` v3 | estrita, **exceto `if`**   | `let`, `letrec`   | léxico                     | funções recursivas  | —      | números + closures             | `if` (expressão), recursão    | dinâmicos (`2 + (1<2)` vale `3`) |

Colunas em que a turma deve dizer, em voz alta, **"ainda não temos"**: estado,
dados compostos (só números e closures) e tipos estáticos.

Células que merecem uma frase de discussão:

- **avaliação de v3:** estrita _exceto_ `if`: forma especial;
- **dados:** closures são dados (os booleans da biblioteca são dados
  codificados como funções);
- **tipos:** a nota sobre números e "booleans" é a semente da Unidade 8.

Tarefa opcional no Classroom: cada estudante justifica **uma célula**.


## Bloco 8: O que ainda não conseguimos escrever (≈ 12 min)

> Esta é a ponte para a Unidade 5. Evitar dizer "estado" antes de a turma
> chegar lá.

Com `letrec` e `if` temos repetição. Mas ela é de um tipo especial: cada
repetição é uma **nova chamada** com **novos valores**. Nunca a _mesma_
variável com valor diferente. Três desafios:

### 8.1 Um contador

Escrever `contador` tal que chamadas sucessivas devolvam `1`, `2`, `3`:

```text
contador()      # 1
contador()      # 2
contador()      # 3
```

Deixar tentar com closure. Eles descobrem que o ambiente capturado é imutável.
Pior: em `aljabr`, uma função com os mesmos argumentos **sempre** devolve o
mesmo valor. `contador()` não pode existir.

### 8.2 Um `enquanto`

```text
enquanto (i < 10) corpo
```

Se nada muda, `i < 10` vale sempre o mesmo: ou o laço não executa nenhuma vez,
ou executa para sempre. Em `aljabr`, repetição **só** existe como recursão.

### 8.3 Reavaliar uma expressão

Por que alguém avaliaria `e` duas vezes? Pela transparência referencial, o
valor é sempre o mesmo: seria desperdício (poderíamos até guardar e reaproveitar
o resultado).

> **Pergunta final:** em que condições faria sentido avaliar a mesma expressão
> duas vezes?
>
> Resposta que queremos: quando o valor pode depender de **quando** a
> avaliação acontece.

### 8.4 Frase de transição

> "Todo o curso até aqui foi sobre uma linguagem em que **quando** não
> importa. Na quarta, vamos perder essa propriedade de propósito, e ver o que
> se ganha e o que se paga."


## Bloco 9: Fechamento e tarefa (≈ 5 min)

### 9.1 Resumo

1. Mostramos o limite de v2 em três paredes (nome, estrita, sem teste) e
   decidimos **como** removê-las em v3: `letrec`, `if` como forma especial e
   comparações.
2. Especificamos v3 nos três níveis; a implementação é a tarefa.
3. Nomeamos o que construímos: funções de primeira classe e **linguagem
   funcional pura**, caracterizada pelo que introduzimos e, principalmente,
   pelo que não introduzimos.

### 9.2 Exercícios de fixação (para a Aula 15)

1. **Implementar `aljabr` v3** a partir das especificações (léxico, EBNF e
   regras), usando a tabela de testes do Bloco 5.5. Ao implementar o `letrec`,
   **anote** qualquer dificuldade que tiver para criar um closure cujo ambiente
   contém o próprio closure e **como** você resolveu isso em Python.
2. Derivar, com as regras, o valor de `if 0 then 1/0 else 7` e explicar por que
   `se(true, 1, 1/0)` dá `erro` mas `if 1 then 1 else 1/0` dá `1`.
3. Escrever, em Python, `soma(n)` (soma de `1` a `n`) usando **apenas funções,
   chamadas e `if`/`else`**: sem atribuição (nem `+=`, nem `:=`), sem
   `nonlocal`/`global` e sem laços.
4. **(Desafio)** Tentar escrever em Python, nas mesmas restrições do item 3,
   uma função `contador` que devolva `1`, `2`, `3` em chamadas sucessivas.
   Anotar **exatamente** onde trava.
5. **(Desafio de design)** Suponha que `aljabr` precisasse aceitar `x := valor`.
   O que teria de mudar na assinatura de `eval(expr, env)`? **Onde** o novo
   valor ficaria guardado? Escrever em poucas linhas; o que acontece se dois
   closures compartilham `x`?
6. **(Opcional)** Derivar `<=`, `>`, `>=` e `!=` em `aljabr` v3 usando `if`.


## Pontos de checagem de entendimento

- **Após o Bloco 2:** a turma consegue listar as quatro propriedades de
  primeira classe usando exemplos dos próprios programas?
- **Após o Bloco 3:** a turma explica, sem ajuda, por que `se(true, 1, 1/0)`
  vale `erro`? E por que `let f = fn (n) => f(n) in f(1)` também?
- **Após o Bloco 4:** a turma articula por que `letrec` é preferível a mudar o
  `let` (o exemplo `let x = x + 1`)?
- **Após o Bloco 5:** a turma enxerga, na **forma** das regras `(If…)`, que só
  um caminho é avaliado? E consegue dizer o que há de circular em `(LetRec)`?
- **Após o Bloco 6:** a turma define transparência referencial com suas
  palavras e explica por que substituição e ambiente coincidem em `aljabr`?
- **Após o Bloco 8:** a turma percebe que o contador **não pode** existir em
  `aljabr`, e não apenas que "é difícil"?


## Ponte para a Aula 15 e ajustes sugeridos ao plano

### Como abrir a Aula 15

- Abrir com os três fracassos do Bloco 8 (2 min) e ir direto às propostas dos
  alunos para o exercício 5.
- A proposta mais provável é **"mutar o dicionário do ambiente"**. Tratar como
  alternativa legítima de design, não como erro. Depois mostrar o que ela não
  resolve bem (aliasing explícito, formalização) e só então apresentar o
  **store** (`ρ: nome → localização`, `σ: localização → valor`) como decisão
  justificada, e não como notação imposta.
- Retomar o `letrec` implementado: quem usou uma atribuição (ou `dict`
  atualizado depois da criação do closure) já usou **estado** na metalinguagem,
  escondido da linguagem-objeto. É o primeiro exemplo de estado do curso.

### Duas observações sobre o plano de aulas

- **Comandos na Aula 15.** O plano atual deixa a discussão _expressão ×
  comando_ para a Aula 16. Como `x := valor` obriga a pergunta "que valor essa
  construção produz?", sugiro plantá-la já na Aula 15 e desenvolvê-la na Aula
  16 com `if` e `enquanto`. Nota: o `if` de v3 é uma **expressão**; na Unidade 6
  teremos o `if` como _comando_. A comparação entre os dois é o melhor
  material para essa discussão.
- **Reavaliação na Aula 16.** O argumento do Bloco 8.3 (só com estado faz
  sentido reavaliar uma expressão) é a justificativa natural para o `enquanto`.
  Vale incluí-lo na motivação da Aula 16: lá ele deixa de ser pergunta e vira
  conclusão.
