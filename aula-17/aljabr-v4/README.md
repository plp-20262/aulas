# Especificação de `aljabr`

A principal mudança na especificação da LP `aljabr` versão `v4` em comparação à
versão `v3` é a inclusão de **tipos algébricos** (valores etiquetados, formados
por soma e produto) e da expressão `match` (casamento de padrões), que permite
desestruturar esses valores. Além disso, o programa de nível superior agora pode
conter declarações de tipos (`type`).

> **aljabr v4 = v3 + tipos algébricos e `match`.** Nenhuma regra de v3 muda,
> exceto um pequeno ajuste em (IfCond), indicado abaixo. A implementação em
> Python **não** é construída nesta aula; este documento é a especificação formal
> que um implementador deveria seguir.

IMPORTANTE: embora as inclusões de v3 (`se`/`if` e `let-rec`) introduzam os
poderes de expressar a _seleção de caminhos de execução_ e de expressar
repetições, através de recursividade explícita. O poder computacional da
linguagem na versão `v2` já era Turing equivalente.

## 1. Léxico

O léxico de v4 retém todos os tokens de v3 e acrescenta quatro novas categorias
léxicas (construtores, pipe, chaves). As palavras reservadas passam a ser dez:

```text
LETREC  ::=  letrec          (v3)
IF      ::=  if              (v3)
THEN    ::=  then            (v3)
ELSE    ::=  else            (v3)
EQEQ    ::=  ==              (v3)
LT      ::=  <               (v3)
CONSTR  ::=  [A-Z][A-Za-z0-9_]*   ← NOVO (construtores e nomes de tipos)
PIPE    ::=  \|              ← NOVO
LBRACE  ::=  \{              ← NOVO
RBRACE  ::=  \}              ← NOVO
```

Palavras reservadas, agora dez: `let`, `in`, `fn`, `letrec`, `if`, `then`,
`else`, `type`, `match` e `_`. O `_` precisa ser reservado porque também casa
com a regra de `NOME`. O `=>` e a vírgula já existem (v2).

As demais categorias léxicas continuam existindo, da mesma forma que eram na
versão `v3`:

```text
POW      ::=  \*\*
ADD      ::=  \+
SUB      ::=  -
MULT     ::=  \*
DIV      ::=  /
INPUT    ::=  \?
LPAREN   ::=  \(
RPAREN   ::=  \)
ARROW    ::=  =>            (v2)
EQUAL    ::=  =
COMMA    ::=  ,             (v2)
INTEIRO  ::=  [0-9]+
NOME     ::=  [a-z_][a-z0-9_]*   (exceto as palavras reservadas)
```

## 2. Sintaxe

Vale mais uma vez a observação sobre notação: os parênteses da _linguagem_ são
`LPAREN`/`RPAREN`; os parênteses `( … )` da EBNF são meta-símbolos.

Abaixo a EBNF atualizada de `aljabr` versão `v4`.

```text
programa  ::= { tipo_decl } exp                                     ← ALTERADO
tipo_decl ::= type CONSTR = variante { PIPE variante }              ← NOVO
variante  ::= CONSTR [ LPAREN params RPAREN ]                       ← NOVO
exp       ::= let NOME = exp in exp
            | letrec NOME = fn LPAREN [ params ] RPAREN => exp in exp
            | fn LPAREN [ params ] RPAREN => exp
            | if exp then exp else exp
            | match exp LBRACE ramo { ramo } RBRACE                 ← NOVO
            | comp
ramo      ::= padrao => exp                                         ← NOVO
padrao    ::= INTEIRO | _ | NOME
            | CONSTR [ LPAREN padrao { , padrao } RPAREN ]          ← NOVO
comp      ::= soma [ ( == | < ) soma ]
soma      ::= termo { ( + | - ) termo }
termo     ::= fator { ( * | / ) fator }
fator     ::= unario [ ** fator ]
unario    ::= [ + | - ] chamada
chamada   ::= atomo { LPAREN [ args ] RPAREN }
atomo     ::= INTEIRO | NOME
            | CONSTR [ LPAREN args RPAREN ]                         ← NOVO
            | LPAREN exp RPAREN
params    ::= NOME { , NOME }
args      ::= exp { , exp }
```

(O restante da gramática, de `comp` a `chamada`, é o de v3.)

Mudanças em relação à `v3`:
1. `programa` agora começa com zero ou mais `tipo_decl`, seguidos de uma `exp`;
2. nascem as produções `tipo_decl`, `variante`, `ramo` e `padrao`;
3. `exp` ganha `match`;
4. `atomo` ganha a construção de valor etiquetado `CONSTR [ ( args ) ]`;
5. `padrao` permite literais inteiros, curinga `_`, variáveis `NOME` e
   construtores aninhados.

A gramática continua LL(1): `LETREC`, `IF`, `FN`, `LET` e `MATCH` decidem a
alternativa de `exp`; `CONSTR` pode iniciar tanto um `atomo` (construção de
valor) quanto um `padrao`; a distinção é feita pelo contexto em que `atomo` ou
`padrao` é derivado.

### Decisões de design codificadas na gramática

- **Construtor × variável pelo léxico.** `Num` é `CONSTR`, `num` é `NOME`.
  Assim, num padrão, um `NOME` sozinho **é sempre variável**, e um `CONSTR`
  sozinho é um construtor sem componentes (`Vazia`). Haskell, ML e Rust usam a
  letra maiúscula do mesmo modo; Python não, e daí vem a armadilha do
  `case Num:` (o nome seria capturado como variável).
- **`CONSTR` seguido de `(` é construção, não aplicação.** O `atomo` consome
  os parênteses antes de `chamada`. Em `Num(2)(3)`, a aplicação de `Num(2)`
  a `3` dá erro em tempo de execução (AppNaoFuncao).
- **Sem `()` vazio.** Variantes sem componentes são escritas `Vazia`, e
  `Vazia()` é erro sintático.
- **O ramo `padrao => exp` não tem separador.** Parece não haver ambiguidade
  (o ramo seguinte começa com `CONSTR`, `NOME`, `_` ou `INTEIRO`, e nenhum
  deles continua uma `exp`), mas **vale conferir ao implementar**.
- **Variáveis distintas em um padrão.** `Add(x, x)` é rejeitado pelo parser.
  Evita decidir o que seria casar o mesmo nome duas vezes.
- **Construtores têm nome único no programa.** O conjunto $\Delta$ de
  declarações ($K/n$: construtor $K$ de aridade $n$) é global. Declarar o
  mesmo construtor duas vezes é erro.
- **O nome do tipo é só documentação.** Em `type Expr = Num(n) | …`, o nome
  `Expr` não aparece em nenhuma regra: a linguagem continua dinamicamente
  tipada. Um `match` pode misturar construtores de tipos diferentes. É um bom
  gancho para a Unidade 8.

### Exemplos de programas mal-formados

| Programa                               | Por quê                                         |
|----------------------------------------|-------------------------------------------------|
| `1 < 2 < 3`                            | `comp` não é associativa                        |
| `if x then 1`                          | `else` obrigatório                              |
| `letrec x = 5 in x`                    | o lado direito de `letrec` precisa ser `fn`     |
| `1 + if 1 then 2 else 3`               | `if` como operando sem parênteses               |
| `let if = 1 in if`                     | `if` é palavra reservada                        |
| `Num()`                                | `Num/1` declarado; `()` com aridade 0 não bate  |
| `match x { }`                          | `match` exige ao menos um ramo                  |
| `match x { Add(a, a) => a }`           | variável repetida no padrão                     |
| `type T = A | A`                       | construtor repetido na declaração de tipo       |
| `type T = vazia`                       | `vazia` é `NOME`, não `CONSTR`                  |
| `let _ = 1 in 2`                       | `_` é palavra reservada                         |
| `Foo(1)`                               | `Foo` não declarado em $\Delta$                 |
| `Cons` (com `Cons/2` declarado)        | forma sem parênteses exige aridade 0            |

## 3. Semântica 

### Domínios semânticos

Valores etiquetados $K(v_1,\ldots,v_n)$ entram em $\mathrm{Val}$:

| Domínio                                                                          | Descrição                                            |
|----------------------------------------------------------------------------------|------------------------------------------------------|
| $ℝ$                                                                              | Os números reais.                                    |
| $\mathrm{Clo} = \mathrm{Var}^* \times \mathrm{Exp} \times \mathrm{Env}$          | _Closures_: (parâmetros, corpo, ambiente de criação) |
| $\mathrm{Tag}$                                                                   | Valores etiquetados $K(v_1,\ldots,v_n)$              |
| $\mathrm{Val} = ℝ ∪ \mathrm{Clo} ∪ \mathrm{Tag} ∪ \\{ \mathtt{erro} \\}$        | Valores possíveis                                    |
| $\mathrm{Env} = \mathrm{Var} ⇀ \mathrm{Val}$                                     | Ambientes                                            |

Um valor etiquetado guarda **valores**, e não localizações. O ambiente $\rho$ e
o julgamento $\langle e, \rho\rangle \Downarrow v$ continuam os de v3.

### Construção de um valor etiquetado

$$
\frac{
  K/n \in \Delta \qquad
  \langle e_i,\rho\rangle \Downarrow v_i \quad (1 \le i \le n)
}{
  \langle K(e_1,\ldots,e_n),\rho\rangle \Downarrow K(v_1,\ldots,v_n)
} \quad \text{(Cons)}
$$

$$
\frac{
  K/n \notin \Delta
}{
  \langle K(e_1,\ldots,e_n),\rho\rangle \Downarrow \mathbf{erro}
} \quad \text{(ConsInvalido)}
$$

Em (ConsInvalido), $K$ não foi declarado **ou** tem outra aridade. A forma sem
parênteses, `K`, é o caso $n = 0$. Como em (AppAridade), a verificação vem
antes de avaliar os argumentos.

### Casamento de um padrão

Não é uma avaliação: é uma relação auxiliar $\mathrm{casa}(p, v) = \theta$, em
que $\theta$ é a coleção das variáveis do padrão com os valores que receberam,
ou $\bot$ se o padrão não casa.

$$
\mathrm{casa}(x, v) = \{x \mapsto v\} \quad \text{(PVar)}
\qquad
\mathrm{casa}(\\_, v) = \\{\ \\} \quad \text{(PCuringa)}
$$

$$
\mathrm{casa}(n, n) = \\{\ \\} \quad \text{(PLit)}
\qquad
\mathrm{casa}(n, v) = \bot \ \ \text{se } v \neq n
$$

$$
\frac{
  \mathrm{casa}(p_i, v_i) = \theta_i \neq \bot \quad (1 \le i \le n)
}{
  \mathrm{casa}(K(p_1,\ldots,p_n),\ K(v_1,\ldots,v_n)) = \theta_1 \cup \cdots \cup \theta_n
} \quad \text{(PCons)}
$$

Em qualquer outro caso, $\mathrm{casa}(K(p_1,\ldots,p_n), v) = \bot$: etiqueta
diferente, aridade diferente, valor que não é etiquetado, ou algum subpadrão
que não casa. (Com $n = 0$, (PCons) não tem premissas: `Vazia` casa com
`Vazia`.)

### Condicional

Observe que só **um** caminho aparece nas premissas:

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
  \langle c,\rho\rangle \Downarrow v_c \qquad v_c \notin ℝ
}{
  \langle \texttt{if}\ c\ \texttt{then}\ e_1\ \texttt{else}\ e_2,\ \rho\rangle \Downarrow \mathbf{erro}
} \quad \text{(IfCond)}
$$

Se a condição avalia para `erro`, vale a convenção de propagação da Aula 12
§4.2. O caminho não escolhido **nunca é avaliado**, logo seus erros e sua
não-terminação nunca acontecem.

**Ajuste em v3.** Com valores etiquetados, a regra (IfCond) passa a cobrir
qualquer condição que não seja número (e não só closures): `if Num(1) then …`
dá `erro`, porque `Num(1) ∉ ℝ`.

### Recursão

A regra define um ambiente em termos de si mesmo:

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

> **Retomada de observação da Aula 12 (§4.1)** Lá dissemos que closures são
> construídos "de dentro para fora" e que isso voltaria com a recursão. Aqui
> o ciclo é **genuíno**: o ambiente contém o closure, que contém o ambiente.
> (Tecnicamente, $\rho_1$ é um ponto fixo; não precisamos desse formalismo.)
>
> Nenhuma outra regra muda. Em particular, (App) continua avaliando o corpo
> em $\rho_0[\ldots]$: é o fato de $\rho_0 = \rho_1$ conter $f$ que faz a
> recursão funcionar.

### Expressão `match`

Escolhe o **primeiro** ramo que casa e avalia **só** o corpo dele, num
ambiente estendido com as variáveis do padrão. Escrevemos $\rho[\theta]$ para
$\rho[x_1 \mapsto u_1,\ldots,x_k \mapsto u_k]$, quando
$\theta = \{x_1 \mapsto u_1,\ldots,x_k \mapsto u_k\}$.

$$
\frac{
  \langle e,\rho\rangle \Downarrow v \qquad
  \mathrm{casa}(p_j, v) = \bot \ \ (j < i) \qquad
  \mathrm{casa}(p_i, v) = \theta \neq \bot \qquad
  \langle e_i,\rho[\theta]\rangle \Downarrow v'
}{
  \langle \mathtt{match}\ e\ \\{p_1 \Rightarrow e_1\ \cdots\ p_m \Rightarrow e_m\\},\rho\rangle \Downarrow v'
} \quad \text{(Match)}
$$

$$
\frac{
  \langle e,\rho\rangle \Downarrow v \qquad
  \mathrm{casa}(p_j, v) = \bot \ \ (1 \le j \le m)
}{
  \langle \mathtt{match}\ e\ \\{p_1 \Rightarrow e_1\ \cdots\ p_m \Rightarrow e_m\\},\rho\rangle \Downarrow \mathbf{erro}
} \quad \text{(MatchNenhum)}
$$

Vale a convenção de propagação de `erro` da Aula 12 (§4.2).

### Operações Semânticas e Operadores

Mais uma vez, para simplificar as regras de inferência, usarei apenas operações
semânticas totais, obtidas através de um _lift_. Ou seja, as operações
retornarão $\mathrm{erro}$ para todo valor do domínio em que a original esteja
indefinida. As funções lifted também devem propagar erros em estilo monádico.
Esta decisão permite eliminar as regras de inferência para lidar com erros de
funções parciais e as regras de propação de erro.

**Notação** Nos referiremos às operações semânticas com a notação
$f_{\text{op}}$ (original) e $f_{\text{op}}^{\uparrow}$ (_lifted_), para à
operação relacionada ao operador $\text{op}$. Por exemplo, para a operação de
soma podemos usar $f_{+}$ (original) e $f_{+}^{\uparrow}$ (_lifted_).

Se assumirmos que cada operação semântica original é uma função parcial

$$
f_{\mathrm{op}} : \mathbb{R} \times \mathbb{R} \rightharpoonup \mathbb{R},
$$

podemos definir sua versão _lifted_ como uma função total

$$
f_{\mathrm{op}}^{\uparrow} :
\mathrm{Val} \times \mathrm{Val}
\to
\mathrm{Val},
$$

em que $\mathrm{Val} = \mathbb{R} \cup \\{ \mathbf{erro} \\}$. A função
_lifted_ propaga $\mathbf{erro}$ e transforma em $\mathbf{erro}$ qualquer
aplicação da operação original para a qual ela não esteja definida:

$$
f_{\mathrm{op}}^{\uparrow}(v_1,v_2) =
\begin{cases}
\mathbf{erro},
  & \text{se } v_1 = \mathbf{erro}\ \text{ou}\ v_2 = \mathbf{erro}, \\
f_{\mathrm{op}}(v_1,v_2),
  & \text{se } v_1,v_2 \in ℝ\ \text{e} \ f_{\mathrm{op}}(v_1,v_2)\mathrel{\downarrow}, \\
\mathbf{erro},
  & \text{caso contrário}.
\end{cases}
$$

Aqui, $f_{\mathrm{op}}(v_1,v_2)\mathrel{\downarrow}$ significa que a função
parcial $f_{\mathrm{op}}$ está definida para o par $(v_1,v_2)$ (notação
convencional de lógica matemática, computabilidade e funções parciais).

**O que não precisa de regra nova:** `Num(2) + 1`, `Num(2) == 1` e afins já
dão `erro`, porque o *lift* das operações (Aula 8) devolve `erro` fora de
$ℝ$. Isso também significa que **não há igualdade estrutural** entre valores
etiquetados (decisão de design: `dataclass` em Python tem; Haskell tem com
`deriving Eq`).

### Regras de Avaliação

#### Regras herdadas de aljabr versão v1

As regras abaixo são transcritas da especificação da versão v1 de `aljabr`.
Ressalvo que usamos usamos o ambiente _lifted_, o que nos permite dispensar a
regra (VarNaoLigada) vista e apresentada na especificação anterior, apenas como
alternativa, caso não usássemos _lift_.

$$
\frac{}{\langle n, \rho \rangle \Downarrow n} \quad \text{(Num)}
\qquad
\frac{\rho(x) = v}{\langle x, \rho \rangle \Downarrow v} \quad \text{(Var)}
$$

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho[x \mapsto v_1] \rangle \Downarrow v_2
}{
  \langle \text{let } x = e_1 \text{ in } e_2, \rho \rangle \Downarrow v_2
} \quad \text{(Let)}
$$

$$
\frac{
  \langle e_1, \rho \rangle \Downarrow v_1 \qquad
  \langle e_2, \rho \rangle \Downarrow v_2
}{
  \langle e_1 \text{ op } e_2, \rho \rangle \Downarrow f_{\mathrm{op}}^{\uparrow}(v_1, v_2)
} \quad \text{(Op)}
$$

(As regras dos operadores unários são análogas.) Lembre que $f^{\uparrow}$ é o
_lift_ da operação parcial $f$:

$$
f^{\uparrow}(v_1, v_2) =
\begin{cases}
f(v_1, v_2) & \text{se } v_1, v_2 \in ℝ \text{ e } (v_1, v_2) \in \mathrm{dom}(f) \\
\mathtt{erro} & \text{caso contrário}
\end{cases}
$$

**Ambiente _lifted_.** Como na especificação anterior, usamos uma versão
_lifted_ de `ρ`: para toda variável `x ∉ dom(ρ)`, definimos `ρ(x) = erro`.
Assim, a regra ($\mathrm{Var}$) cobre também as variáveis não vinculadas, e não
precisamos de uma regra à parte para isso.

**Convenção de propagação de erro.** As regras desta unidade descrevem apenas
o caso em que as premissas produzem valores "de verdade" (elementos de
$ℝ ∪ \mathrm{Clo} ∪ \mathrm{Tag}$). Para os demais casos, adotamos uma
convenção, declarada uma única vez, válida para todas as regras:

> se alguma premissa da forma $⟨e, ρ⟩ ⇓ v$ produz $v = \mathbf{erro}$, a regra
> não se aplica e a conclusão é $\mathbf{erro}$.

Esta convenção abrevia as regras de propagação que teríamos que escrever uma a
uma, para cada construção da linguagem. Trata-se do equivalente formal ao
tratamento monádico de erros da implementação: o erro interrompe a avaliação
assim que aparece (erros são **estritos**). Em particular, `let x = 1/0 in 5`
vale `erro`, e não `5`.

#### Regras de definição e aplicação de funções (herdadas de aljabr v2)

**Criação de closure.** Um lambda avalia para um closure que captura e
"congela" o ambiente corrente:

$$
\frac{}{
  \langle \texttt{fn}\ (p_1, \ldots, p_n) \Rightarrow e,\ \rho \rangle
  \Downarrow
  \mathsf{clo}((p_1, \ldots, p_n),\ e,\ \rho)
} \quad \text{(Lam)}
$$

**Aplicação.**

$$
\frac{
  \begin{matrix}
  \langle e_f, \rho \rangle \Downarrow \mathsf{clo}((p_1, \ldots, p_n), e_b, \rho_0) \\
  \rule{0pt}{6ex}
  \langle a_i, \rho \rangle \Downarrow v_i \quad (1 \le i \le n) \\
  \rule{0pt}{6ex}
  \langle e_b, \rho_0[p_1 \mapsto v_1, \ldots, p_n \mapsto v_n] \rangle \Downarrow v \\
  \rule{0pt}{3ex}
  \end{matrix}
}{
  \langle e_f(a_1, \ldots, a_n), \rho \rangle \Downarrow v
} \quad \text{(App)}
$$

#### Regras de erro da aplicação

Há duas maneiras de uma aplicação **originar** um erro, uma por regra. Os erros
que apenas se _propagam_ (um argumento que avalia para `erro`, ou um corpo que
resulta em `erro`) não precisam de regra própria: são cobertos pela convenção
de erros já mencionada e pela própria regra (App), cujo valor é o valor do
corpo.

**Aplicar algo que não é função:**

$$
\frac{
  \langle e_f, \rho \rangle \Downarrow v_f \qquad v_f \notin \mathrm{Clo}
}{
  \langle e_f(a_1, \ldots, a_m),\ \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(AppNaoFuncao)}
$$

**Número errado de argumentos:**

$$
\frac{
  \langle e_f, \rho \rangle \Downarrow \mathsf{clo}((p_1, \ldots, p_n),\ e_b,\ \rho_0)
  \qquad m \neq n
}{
  \langle e_f(a_1, \ldots, a_m),\ \rho \rangle \Downarrow \mathbf{erro}
} \quad \text{(AppAridade)}
$$

Observe duas escolhas de projeto:

- a **aridade é verificada antes** de avaliar os argumentos (passo 2 antes do
  passo 3 da Aula 09);
- `erro` não pode ser passado como argumento: um argumento que avalia para
  `erro` interrompe a aplicação, pela convenção de propagação da Seção 4.2. Assim,
  as três regras de aplicação, (App), (AppNaoFuncao) e (AppAridade), são
  mutuamente exclusivas.

#### Ligações rápidas com o `match` (Bloco 3 da aula)

| Parte da regra | Pergunta do Bloco 3 |
|---|---|
| 1ª premissa de (Match) | 1. Qual é o valor? |
| $\mathrm{casa}(p_j, v) = \bot$ para $j < i$ | 2. Ramos tentados de cima para baixo (a ordem **está** na regra; por isso o `match` é determinístico) |
| $\mathrm{casa}(p_i, v) = \theta$ | 3. Casar = testar a forma e extrair componentes |
| $\rho[\theta]$ | 4. O corpo vê as variáveis do padrão, **só** nele |
| só aparece $e_i$ como premissa | os outros ramos nunca são avaliados (como no `if`, Aula 14) |
| (MatchNenhum) | e se nada casa? Em `aljabr` v4, é `erro` |

Duas conexões rápidas:

- **Closures dentro do ramo:** em `Num(n) => fn (x) => x + n`, o closure
  captura $\rho[\theta]$, com `n` vinculado. Nenhuma regra nova.
- **`if` é um `match` quase:** `if c then a else b` se comporta como
  `match c { 0 => b  _ => a }`, exceto quando `c` não é número (o `if` dá
  `erro`, o `match` cai no `_`). Boa ligação com o açúcar sintático da Aula 15.

### 4.3 Regras de avaliação → eval

A assinatura de `eval` não muda: `eval(ast, env) -> Val`. Cada regra vira uma
cláusula. Para a regra (App), leia as premissas como instruções:

| Parte da regra                                            | O que o `eval` faz                                              |
|-----------------------------------------------------------|-----------------------------------------------------------------|
| $\langle e_f, \rho \rangle \Downarrow \mathsf{clo}(\ldots)$ | avalia `e_f` em `env` e verifica que o resultado é um closure   |
| $m \neq n$                                                | compara o número de argumentos com o de parâmetros              |
| $\langle a_i, \rho \rangle \Downarrow v_i$                | avalia cada argumento em `env`, o ambiente **de chamada**       |
| $\rho_0[p_1 \mapsto v_1, \ldots]$                         | cria um novo dicionário a partir do ambiente **do closure**     |
| $\langle e_b, \ldots \rangle \Downarrow v$                | avalia o corpo no novo ambiente e devolve o resultado           |

E para a regra (Lam): empacotar `(params, corpo, env)` em um closure, sem
avaliar o corpo. Um closure é uma tripla; em Python, uma tupla ou uma
`dataclass` imutável com três campos serve bem.

Para a regra (Match), as premissas se traduzem como:

| Parte da regra (Match)                                  | O que o `eval` faz                                                 |
|---------------------------------------------------------|--------------------------------------------------------------------|
| $\langle e,\rho\rangle \Downarrow v$                    | avalia o alvo do `match` em `env`                                  |
| $\mathrm{casa}(p_j, v) = \bot\ (j < i)$                 | tenta os ramos anteriores; nenhum casa                             |
| $\mathrm{casa}(p_i, v) = \theta \neq \bot$              | encontra o primeiro ramo que casa e extrai as vinculações $\theta$ |
| $\langle e_i,\rho[\theta]\rangle \Downarrow v'$         | avalia o corpo do ramo com o ambiente estendido por $\theta$       |
| (MatchNenhum)                                           | nenhum ramo casa → devolve `Erro`                                  |

Observe que as regras `AppNaoFuncao` e `AppAridade` correspondem aos dois
pontos em que o `eval` _origina_ um `Erro` na aplicação. Já a propagação de
erro (um argumento, ou o corpo, que resulta em `Erro`) é a convenção da §4.2:
o `eval` apenas devolve o erro recebido, sem prosseguir. E lembre que o _lift_
das operações já trata o caso de funções em expressões aritméticas.

### Derivação exemplo

Para $\Delta = \{\texttt{Num}/1, \texttt{Add}/2, \texttt{Mul}/2\}$ e
`match Add(Num(2), Num(3)) { Num(n) => n  Add(a, b) => b }` em $\rho = \emptyset$
(o resultado é `Num(3)`):

```text
⟨match … , ∅⟩ ⇓ Num(3)                                              (Match)
├─ ⟨Add(Num(2), Num(3)), ∅⟩ ⇓ Add(Num(2), Num(3))                    (Cons)
│  ├─ ⟨Num(2), ∅⟩ ⇓ Num(2)                                           (Cons, com ⟨2, ∅⟩ ⇓ 2 por (Num))
│  └─ ⟨Num(3), ∅⟩ ⇓ Num(3)                                           (Cons, idem)
├─ casa(Num(n), Add(Num(2), Num(3))) = ⊥                             (etiqueta diferente)
├─ casa(Add(a, b), Add(Num(2), Num(3))) = {a ↦ Num(2), b ↦ Num(3)}   (PCons, PVar, PVar)
└─ ⟨b, ∅[a ↦ Num(2), b ↦ Num(3)]⟩ ⇓ Num(3)                           (Var)
```

Sem store, sem localizações novas: a derivação cabe em meia tela. Comparar com
a derivação de `let` da Aula 8.
