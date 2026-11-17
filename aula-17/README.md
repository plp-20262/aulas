# Aula 17 — 16/Nov — Fecho da Unidade 6 + Unidade 7 (1/3): Tipos Algébricos e `aljabr` v4

## Bloco 0 — Fecho da Aula 16: o comando `while` (≈ 12 min)

**Gancho.** Na Aula 14 (§8), `enquanto (i < 10) corpo` não fazia sentido em `aljabr`: sem mudança de estado, `i < 10` sempre vale o mesmo. Agora há *store*: avaliar `i < 10` duas vezes pode dar resultados diferentes. Reavaliar uma expressão deixou de ser desperdício e passou a ser **o que faz o programa progredir**.

> **Pergunta à turma:** o que precisa acontecer entre duas avaliações da condição para o laço terminar? *(O corpo precisa modificar o store.)*

**Sintaxe.** `while` é um comando: não produz valor, e o corpo é uma sequência de comandos sem expressão final. É a sexta palavra reservada. A condição é numérica (`0` é falso) e closure na condição dá `erro`.

```text
comando    ::= func_decl | var_decl ; | atribuicao ; | while_cmd | exp ;
while_cmd  ::= while exp bloco_cmd            ← NOVO (sem ";")
bloco_cmd  ::= LBRACE { comando } RBRACE      ← NOVO
```

**Semântica.** A relação de comandos é $\langle c,\rho,\sigma\rangle \rightarrow \langle\rho',\sigma'\rangle$. O corpo executa em sequência e **descarta o ambiente final**; o store persiste.

$$
\frac{
  \langle c_1,\rho,\sigma_0\rangle \rightarrow \langle\rho_1,\sigma_1\rangle \quad\cdots\quad
  \langle c_n,\rho_{n-1},\sigma_{n-1}\rangle \rightarrow \langle\rho_n,\sigma_n\rangle
}{
  \langle \{c_1 \dots c_n\},\rho,\sigma_0\rangle \Downarrow_{s} \sigma_n
} \quad \text{(BlocoCmd)}
$$

$$
\frac{
  \langle c,\rho,\sigma\rangle \Downarrow \langle 0,\sigma_1\rangle
}{
  \langle \mathtt{while}\ c\ b,\rho,\sigma\rangle \rightarrow \langle\rho,\sigma_1\rangle
} \quad \text{(WhileFalso)}
$$

$$
\frac{
  \langle c,\rho,\sigma\rangle \Downarrow \langle n,\sigma_1\rangle \ (n\in ℝ,\ n\neq 0) \qquad
  \langle b,\rho,\sigma_1\rangle \Downarrow_{s} \sigma_2 \qquad
  \langle \mathtt{while}\ c\ b,\rho,\sigma_2\rangle \rightarrow \langle\rho,\sigma_3\rangle
}{
  \langle \mathtt{while}\ c\ b,\rho,\sigma\rangle \rightarrow \langle\rho,\sigma_3\rangle
} \quad \text{(WhileVerd)}
$$

$$
\frac{
  \langle c,\rho,\sigma\rangle \Downarrow \langle v_c,\sigma_1\rangle \qquad v_c\in\mathrm{Clo}
}{
  \langle \mathtt{while}\ c\ b,\rho,\sigma\rangle \rightarrow \mathbf{erro}
} \quad \text{(WhileCondFuncao)}
$$

**Pontos a comentar (um minuto cada):**

1. A 3ª premissa de (WhileVerd) contém o próprio `while`: a regra é recursiva, e é isso que faz o laço repetir.
2. O store viaja de premissa em premissa ($\sigma \to \sigma_1 \to \sigma_2 \to \sigma_3$) e carrega o progresso do laço.
3. A semântica passa a ser **parcial**: em `while 1 { }` não existe derivação. É a primeira vez que a não-terminação aparece nas regras.
4. O ambiente não muda: um `var` dentro do corpo não é visível depois do laço.

**Exemplo** (tabela de rastreamento, como na Aula 1):

```text
var i := 0;
var soma := 0;
while i < 5 { soma := soma + i; i := i + 1; }
soma                     // 10
```

| Iteração | `i` antes | `i < 5` | `soma` depois |
|----------|-----------|---------|---------------|
| 1 | 0 | 1 | 0 |
| 2 | 1 | 1 | 1 |
| 3 | 2 | 1 | 3 |
| 4 | 3 | 1 | 6 |
| 5 | 4 | 1 | 10 |
| fim | 5 | 0 | 10 |

Cada linha é uma aplicação de (WhileVerd); a última é (WhileFalso).


## Bloco 1 — Problema e decisão de design (≈ 10 min)

### 1.1 O problema: só números e funções

Em `aljabr` v3 e em `algora`, o domínio de valores é

$$
\mathrm{Val} = ℝ \cup \mathrm{Clo} \cup \{ \mathbf{erro} \}
$$

Temos funções de primeira classe, recursão (e, em `algora`, estado e laços), mas **dados compostos** só existem codificados com funções (os booleans da Aula 12). Como representar:

- uma coordenada $(x, y)$;
- uma forma geométrica que é um círculo (raio) **ou** um retângulo (largura e altura);
- o resultado de uma divisão segura: `Ok(valor)` **ou** `Erro(mensagem)`;
- uma lista de números;
- a **AST do nosso próprio interpretador** (`Num`, `Add`, `Mul`, …)?

> **Pergunta central da Unidade 7:** como uma linguagem permite modelar dados compostos e as operações que agem sobre eles?

### 1.2 A decisão de design: dois caminhos, duas linguagens

Há (pelo menos) duas respostas clássicas, e **ambas são legítimas**. O curso vai estudar as duas, cada uma numa linguagem concreta:

| | **Caminho 1: tipos algébricos** | **Caminho 2: objetos** |
|---|---|---|
| Ideia | dados são valores **transparentes**, formados por soma e produto; as operações são funções **separadas** dos dados | dados e operações ficam **juntos**; o objeto tem identidade, estado e esconde a representação |
| Linguagem do curso | **`aljabr` v4** (hoje: especificação) | **`algora`** com objetos (Aulas 18 e 19) |
| Parte de | `aljabr` v3 (puramente funcional) | `algora` (estado mutável) |

> **IMPORTANTE:** a divisão não é um veredito sobre qual caminho é melhor. Linguagens importantes escolheram o Caminho 1 (ML, Haskell, Rust), outras o Caminho 2 (Smalltalk, Java), e muitas modernas misturam os dois (Python, Scala, Kotlin).

> **Ressalva honesta:** `aljabr` v4 e `algora` diferem em **mais** do que a modelagem de dados (`algora` tem estado e comandos, `aljabr` v4 não). A comparação que faremos é sobre **como cada caminho organiza dados e operações**, e não sobre as linguagens inteiras.


## Bloco 2 — A álgebra dos tipos (≈ 15 min)

O nome vem da Matemática Discreta: compomos tipos com **produto cartesiano** e **união disjunta (soma)**.

### 2.1 Tipo produto ($A \times B$): "E"

Agrupa valores que existem **ao mesmo tempo**: registros, `struct`, tuplas.

$$
\text{Ponto} = ℝ \times ℝ
$$

Por que "produto"? Se `Bit` tem 2 valores e `Bool` tem 2 valores, o par `(Bit, Bool)` tem $2 \times 2 = 4$ valores.

### 2.2 Tipo soma ($A + B$): "OU" com etiqueta

Um valor é **exatamente uma** dentre várias alternativas. Cada alternativa tem uma **etiqueta** (construtor) e seus próprios dados.

$$
\text{Forma} = \text{Circulo}(ℝ) \ \mid\  \text{Retangulo}(ℝ \times ℝ)
$$

$$
\text{Resultado} = \text{Ok}(ℝ) \ \mid\  \text{Erro}(\text{String})
$$

> *Callback à Aula 2:* lá improvisamos `Ast | Erro` com um alias de `str`. Um tipo soma é a forma correta de dizer "ou uma AST, ou um erro".

Por que "soma"? Se `Sinal = Parado | Movendo(v)` e $v$ tem $|V\ |$ valores
possíveis, o tipo tem $1 + |V\ |$ valores.

### 2.3 Tipos recursivos: soma + produto + recursão

$$
\text{Lista} = \text{Vazia} \ \mid\  \text{Cons}(ℝ,\  \text{Lista})
$$

$$
\text{Expr} = \text{Num}(ℝ) \ \mid\  \text{Add}(\text{Expr},\  \text{Expr}) \ \mid\  \text{Mul}(\text{Expr},\  \text{Expr})
$$

> **Conexão com o curso:** no interpretador de `aljabr-v3` nós já definimos um tipo algébrico recursivo: `Ast`. Faltava só dar nome ao que fizemos.
>
> **Conexão com `aljabr`:** os booleans da Aula 12 (`true = fn (a, b) => a`) eram dados **codificados** como funções. Em `aljabr` v4, `Cons(1, Vazia)` será um dado nativo.


## Bloco 3 — `match`, passo a passo (≈ 20 min)

Criar um valor algébrico é fácil: chamamos o construtor, como em `Add(Num(2), Num(3))`. A pergunta é a inversa: **dado um valor de um tipo soma, como saber qual variante ele é e como extrair seus componentes?** A resposta é o **casamento de padrões** (*pattern matching*).

> Acredito que no curso, vocês não são estimulados a usar ADTs. Em p1 sei que não chegamos a mostrar modelagem de dados. E em p2, acredito que o foco seja exclusivamente em OO. Assim, vocês não devem ter usado `match`. Vamos devagar, então,  com um exemplo ao vivo em cada etapa.

### 3.1 Um `match` responde a quatro perguntas, nesta ordem

1. **Qual é o valor?** Avalia-se a expressão alvo (`e` em `match e`) até obter um valor.
2. **Qual ramo tentar?** Os ramos são tentados **de cima para baixo**, um por vez.
3. **O valor casa com o padrão do ramo?** Casar é um teste da **forma** do valor ("é um `Add` com dois componentes?") e, ao mesmo tempo, uma **extração** (guardar os componentes em nomes).
4. **E então?** No **primeiro** ramo que casa, o corpo é avaliado com os nomes extraídos vinculados, como num `let`. Os demais ramos **nunca são avaliados**. Se nenhum casa, o `match` falha (o que "falhar" significa é decisão de design; ver Bloco 5).

### 3.2 Os padrões, do mais simples ao mais rico

Demonstrar cada um no interpretador Python (`python3`), com o tipo `Expr` do Bloco 5.1.

| Padrão | Casa quando… | Vincula? | Em `aljabr` v4 |
|---|---|---|---|
| **variável** | sempre | sim, ao valor inteiro | `x` |
| **curinga** | sempre | não | `_` |
| **literal** | o valor é igual ao literal | não | `0` |
| **construtor** | a etiqueta coincide **e** cada subpadrão casa com o componente correspondente | o que os subpadrões vincularem | `Add(a, b)` |
| **aninhado** | idem, recursivamente | idem | `Add(Num(0), x)` |

O padrão aninhado mostra que o `match` faz mais que comparar etiquetas. Em Python:

```python
def simplifica(e):
    match e:
        case Add(Num(0), x):     # 0 + x  ->  x
            return x
        case Mul(Num(1), x):     # 1 * x  ->  x
            return x
        case Mul(Num(0), _):     # 0 * qualquer coisa  ->  0
            return Num(0)
        case _:                  # nenhum dos anteriores: não muda
            return e
```

E o mesmo programa em `aljabr` v4 (sintaxe do Bloco 4):

```text
type Expr = Num(n) | Add(a, b) | Mul(a, b)

let simplifica = fn (e) =>
  match e {
    Add(Num(0), x) => x
    Mul(Num(1), x) => x
    Mul(Num(0), _) => Num(0)
    _              => e
  }
in simplifica(Add(Num(0), Num(7)))              # Num(7)
```

### 3.3 Rastreando um `match` à mão (estilo tabela de rastreamento)

Valor alvo: `Add(Num(2), Num(3))`, com `avalia` do Bloco 5.1.

| Ramo | Padrão | Compara | Resultado |
|------|--------|---------|-----------|
| 1 | `Num(n)` | etiqueta `Add` ≠ `Num` | **não casa**; nada vinculado |
| 2 | `Add(a, b)` | etiqueta `Add` = `Add`; `a` casa com `Num(2)`; `b` casa com `Num(3)` | **casa**; `a ↦ Num(2)`, `b ↦ Num(3)` |
| 3 | `Mul(a, b)` | (não é tentado) | — |

Depois: avalia-se o corpo do ramo 2, `avalia(a) + avalia(b)`, com `a` e `b` vinculados, e o resultado é `5`.

### 3.4 Três perguntas para a turma

> **1. A ordem dos ramos importa?** Coloque `case _:` antes dos outros em `simplifica`. *(Sim: o primeiro que casa vence, e o curinga casa com tudo.)*
>
> **2. É possível escrever isso sem `match`?** Tente com `isinstance` e `if` em cascata:
>
> ```python
> if isinstance(e, Add) and isinstance(e.esq, Num) and e.esq.valor == 0:
>     x = e.dir
>     return x
> ```
>
> O `match` junta **teste da forma** e **extração dos componentes** numa só construção. Parece o açúcar sintático da Aula 15, mas com padrões aninhados a tradução já não é simples.
>
> **3. Quais nomes existem depois do `match`?** *(Em Python, as variáveis do padrão são variáveis comuns da função e continuam existindo depois do `match`. Em `aljabr` v4 (regra Match), existem só no corpo do ramo, como num `let`. É uma diferença de design; ver Bloco 5.)*


## Bloco 4 — Especificação formal de `aljabr` v4 (≈ 15 min)

> `aljabr` v4 = v3 + tipos algébricos e `match`. Nenhuma regra de v3 muda, exceto um pequeno ajuste em (IfCond), indicado abaixo. A implementação **não** é construída em aula.

### 4.1 Léxico e sintaxe

**Léxico.** Uma nova categoria e novos tokens:

```text
CONSTR  ::=  [A-Z][A-Za-z0-9_]*       ← NOVO (construtores e nomes de tipos)
PIPE    ::=  \|                       ← NOVO
LBRACE  ::=  \{      RBRACE ::= \}    ← NOVOS
```

Palavras reservadas, agora dez: `let`, `in`, `fn`, `letrec`, `if`, `then`, `else`, **`type`**, **`match`** e **`_`**. O `_` precisa ser reservado porque também casa com a regra de `NOME`. O `=>` e a vírgula já existem (Aula 11).

**Sintaxe (EBNF)**, com os parênteses da linguagem escritos `LPAREN`/`RPAREN`:

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
atomo     ::= INTEIRO | NOME
            | CONSTR [ LPAREN args RPAREN ]                         ← NOVO
            | LPAREN exp RPAREN
```

(O restante da gramática, de `comp` a `chamada`, é o de v3.)

**Decisões de design codificadas aqui:**

- **Construtor × variável pelo léxico.** `Num` é `CONSTR`, `num` é `NOME`. Assim, num padrão, um `NOME` sozinho **é sempre variável**, e um `CONSTR` sozinho é um construtor sem componentes (`Vazia`). Haskell, ML e Rust usam a letra maiúscula do mesmo modo; Python não, e daí vem a armadilha do `case Num:` (Bloco 5).
- **`CONSTR` seguido de `(` é construção, não aplicação.** O `atomo` consome os parênteses antes de `chamada`. Em `Num(2)(3)`, a aplicação de `Num(2)` a `3` dá erro em tempo de execução (AppNaoFuncao).
- **Sem `()` vazio.** Variantes sem componentes são escritas `Vazia`, e `Vazia()` é erro sintático.
- **O ramo `padrao => exp` não tem separador.** Parece não haver ambiguidade (o ramo seguinte começa com `CONSTR`, `NOME`, `_` ou `INTEIRO`, e nenhum deles continua uma `exp`), mas **vale conferir ao implementar**.
- **Variáveis distintas em um padrão.** `Add(x, x)` é rejeitado pelo parser. Evita decidir o que seria casar o mesmo nome duas vezes.
- **Construtores têm nome único no programa.** O conjunto $\Delta$ de declarações ($K/n$: construtor $K$ de aridade $n$) é global.
- **O nome do tipo é só documentação.** Em `type Expr = Num(n) | …`, o nome `Expr` não aparece em nenhuma regra: a linguagem continua dinamicamente tipada. Um `match` pode misturar construtores de tipos diferentes. É um bom gancho para a Unidade 8.

### 4.2 Domínios semânticos

Valores etiquetados $K(v_1,\ldots,v_n)$ entram em $\mathrm{Val}$:

$$
\mathrm{Val} = ℝ \cup \mathrm{Clo} \cup \mathrm{Tag} \cup \{ \mathbf{erro} \}
$$

Um valor etiquetado guarda **valores**, e não localizações. O ambiente $\rho$ e o julgamento $\langle e, \rho\rangle \Downarrow v$ continuam os de v3.

### 4.3 Regras

**Construção de um valor:**

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

Em (ConsInvalido), $K$ não foi declarado **ou** tem outra aridade. A forma sem parênteses, `K`, é o caso $n = 0$. Como em (AppAridade), a verificação vem antes de avaliar os argumentos.

**Casamento de um padrão** com um valor. Não é uma avaliação: é uma relação auxiliar $\mathrm{casa}(p, v) = \theta$, em que $\theta$ é a coleção das variáveis do padrão com os valores que receberam, ou $\bot$ se o padrão não casa.

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

Em qualquer outro caso, $\mathrm{casa}(K(p_1,\ldots,p_n), v) = \bot$: etiqueta diferente, aridade diferente, valor que não é etiquetado, ou algum subpadrão que não casa. (Com $n = 0$, (PCons) não tem premissas: `Vazia` casa com `Vazia`.)

**A expressão `match`.** Escolhe o **primeiro** ramo que casa e avalia **só** o corpo dele, num ambiente estendido com as variáveis do padrão. Escrevemos $\rho[\theta]$ para $\rho[x_1 \mapsto u_1,\ldots,x_k \mapsto u_k]$, quando $\theta = \{x_1 \mapsto u_1,\ldots,x_k \mapsto u_k\}$.

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

**Um ajuste em v3.** Com valores etiquetados, a regra (IfCond) da Aula 14 passa a cobrir qualquer condição que não seja número (e não só closures):

$$
\frac{
  \langle c,\rho\rangle \Downarrow v_c \qquad v_c \notin ℝ
}{
  \langle \mathtt{if}\ c\ \mathtt{then}\ e_1\ \mathtt{else}\ e_2,\ \rho\rangle \Downarrow \mathbf{erro}
} \quad \text{(IfCond)}
$$

**O que não precisa de regra nova:** `Num(2) + 1`, `Num(2) == 1` e afins já dão `erro`, porque o *lift* das operações (Aula 8) devolve `erro` fora de $ℝ$. Isso também significa que **não há igualdade estrutural** entre valores etiquetados (decisão de design: `dataclass` em Python tem; Haskell tem com `deriving Eq`).

**O que ler nas regras** (ligar com o Bloco 3):

| Parte da regra | Pergunta do Bloco 3 |
|---|---|
| 1ª premissa de (Match) | 1. Qual é o valor? |
| $\mathrm{casa}(p_j, v) = \bot$ para $j < i$ | 2. Ramos tentados de cima para baixo (a ordem **está** na regra; por isso o `match` é determinístico) |
| $\mathrm{casa}(p_i, v) = \theta$ | 3. Casar = testar a forma e extrair componentes |
| $\rho[\theta]$ | 4. O corpo vê as variáveis do padrão, **só** nele |
| só aparece $e_i$ como premissa | os outros ramos nunca são avaliados (como no `if`, Aula 14) |
| (MatchNenhum) | e se nada casa? Em `aljabr` v4, é `erro` |

Duas conexões rápidas:

- **Closures dentro do ramo:** em `Num(n) => fn (x) => x + n`, o closure captura $\rho[\theta]$, com `n` vinculado. Nenhuma regra nova.
- **`if` é um `match` quase:** `if c then a else b` se comporta como `match c { 0 => b  _ => a }`, exceto quando `c` não é número (o `if` dá `erro`, o `match` cai no `_`). Boa ligação com o açúcar sintático da Aula 15.

### 4.4 Derivação (se houver tempo)

Para $\Delta = \{\texttt{Num}/1, \texttt{Add}/2, \texttt{Mul}/2\}$ e `match Add(Num(2), Num(3)) { Num(n) => n  Add(a, b) => b }` em $\rho = \emptyset$ (o resultado é `Num(3)`):

```text
⟨match … , ∅⟩ ⇓ Num(3)                                              (Match)
├─ ⟨Add(Num(2), Num(3)), ∅⟩ ⇓ Add(Num(2), Num(3))                    (Cons)
│  ├─ ⟨Num(2), ∅⟩ ⇓ Num(2)                                           (Cons, com ⟨2, ∅⟩ ⇓ 2 por (Num))
│  └─ ⟨Num(3), ∅⟩ ⇓ Num(3)                                           (Cons, idem)
├─ casa(Num(n), Add(Num(2), Num(3))) = ⊥                             (etiqueta diferente)
├─ casa(Add(a, b), Add(Num(2), Num(3))) = {a ↦ Num(2), b ↦ Num(3)}   (PCons, PVar, PVar)
└─ ⟨b, ∅[a ↦ Num(2), b ↦ Num(3)]⟩ ⇓ Num(3)                           (Var)
```

Sem store, sem localizações novas: a derivação cabe em meia tela. Comparar com a derivação de `let` da Aula 8.


## Bloco 5 — Discussão (≈ 20 min)

### 5.1 Python na prática (demonstração ao vivo)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Num:
    valor: int

@dataclass(frozen=True)
class Add:
    esq: "Expr"
    dir: "Expr"

@dataclass(frozen=True)
class Mul:
    esq: "Expr"
    dir: "Expr"

Expr = Num | Add | Mul          # tipo soma, por união

def avalia(e: Expr) -> int:
    match e:
        case Num(n):    return n
        case Add(a, b): return avalia(a) + avalia(b)
        case Mul(a, b): return avalia(a) * avalia(b)

print(avalia(Mul(Add(Num(2), Num(3)), Num(4))))    # 20
```

Pontos a observar:

1. `Num`, `Add` e `Mul` são **dados puros**, sem métodos. Toda a lógica de avaliação está **fora** deles.
2. `@dataclass` gera `__match_args__`, e é isso que permite o padrão posicional `Add(a, b)`. (Sem ele, só funcionaria `Add(esq=a, dir=b)`.)
3. `frozen=True` impede mutação dos campos: é assim que Python **emula** a imutabilidade dos valores etiquetados de `aljabr` v4.
4. **Nova operação, sem tocar nas classes:**

```python
def mostra(e: Expr) -> str:
    match e:
        case Num(n):    return str(n)
        case Add(a, b): return f"({mostra(a)} + {mostra(b)})"
        case Mul(a, b): return f"({mostra(a)} * {mostra(b)})"
```

E a lista do Bloco 2 (o `tamanho` em `aljabr` v4 está no fim deste arquivo):

```python
@dataclass(frozen=True)
class Vazia: pass

@dataclass(frozen=True)
class Cons:
    cabeca: int
    cauda: "Lista"

Lista = Vazia | Cons

def tamanho(xs: Lista) -> int:
    match xs:
        case Vazia():        return 0
        case Cons(_, resto): return 1 + tamanho(resto)
```

### 5.2 Armadilhas do `match` em Python (e decisões de design por trás delas)

| Armadilha | O que acontece em Python | Em `aljabr` v4 | Decisão de design |
|---|---|---|---|
| **Esquecer um ramo** (retire o `Mul` de `avalia`) | o `match` não casa, **não levanta erro** e a função devolve `None`; o erro aparece longe, quando alguém usa o `None` | `erro` imediato (MatchNenhum) | o que fazer quando nada casa? |
| **`case Num:`** (sem parênteses) | `Num` aqui é um **nome** que captura qualquer valor, e não a classe | impossível: `Num` é `CONSTR`, nunca variável | como distinguir variável de construtor? Python: pelos parênteses; `aljabr`: pelo léxico |
| **Ordem dos ramos** | o primeiro que casa vence | idem, e a ordem está na regra | — |
| **Escopo** | as variáveis do padrão continuam existindo depois do `match` | valem só no corpo do ramo | onde vivem as variáveis do padrão? |

**Verificação de exaustividade.** Em Python, ferramentas externas recuperam parte do que linguagens estáticas fazem. Com `case _: assert_never(e)` (módulo `typing`, Python ≥ 3.11), um verificador como `mypy` ou `pyright` acusa, **antes de executar**, a variante esquecida. Python em si, sem essas ferramentas, não verifica nada.

> **Menção apenas:** esse tipo de checagem é de **tipos estáticos**. O verificador da Unidade 8 cobre aritmética + funções e **não** verifica exaustividade de `match`. O tema só reaparece como menção. Em `aljabr` v4, o nome do tipo (`Expr`) é o que permitiria essa checagem no futuro: com ele, o verificador saberia quais são **todas** as variantes.

### 5.3 Linguagens reais (menção, 2–3 min)

- Em **Rust**, **Haskell**, **OCaml** e **ML**, o tipo algébrico é **nativo** (`enum` em Rust, `data` em Haskell), e não emulado sobre classes. O compilador **recusa** um `match` não exaustivo. É um suporte mais direto e mais completo que o de Python, e a sintaxe de `aljabr` v4 (construtores com maiúscula, `match` com ramos) vem dessa família.
- Um exemplo bem conhecido: o tipo `Result` de Rust é exatamente a soma `Ok(valor) | Err(erro)` do Bloco 2, e o tratamento de erros da linguagem inteira é feito com ele. É a versão "de verdade" do que improvisamos na Aula 2.
- Linguagens mais recentes de outras famílias (Java recente, Kotlin, Scala, Python ≥ 3.10) vêm incorporando versões desse mecanismo: um sinal de que os dois caminhos de design **convivem**.

### 5.4 Relação com a Orientação a Objetos (menção; o detalhe é para as Aulas 18 e 19)

Vocês já conhecem OO, e é natural a pergunta: *"isso não é só OO com outro nome?"*. Duas ideias para guardar:

1. **São visões alternativas para fins semelhantes**: modelar dados compostos, com variantes, e as operações que agem sobre eles. Muitos problemas podem ser resolvidos pelos dois caminhos. É por isso que a AST do curso pode ser escrita das duas formas.
2. **Mas as respostas são diferentes**, e não são meras variações uma da outra:

| Pergunta | Tipos algébricos (`aljabr` v4) | Objetos (`algora`, Aula 18) |
|---|---|---|
| Onde fica o comportamento? | **fora** dos dados, em funções com `match` | **dentro** dos dados, como métodos |
| Como se escolhe o que executar? | inspecionando a forma do valor (`match`) | despacho a partir do próprio objeto |
| A estrutura é visível? | sim, qualquer função desestrutura o valor | não, o objeto pode escondê-la (encapsulamento) |

> **Plantar, sem resolver** (volta na Aula 19): o que é fácil e o que é difícil quando o programa evolui? Acrescentar uma **operação** nova (como `mostra`) a uma AST foi trivial acima, sem tocar nas classes. Acrescentar uma **variante** nova (como `Pot`) exigiria rever todas as funções com `match`. Com objetos, é o contrário. É o chamado *problema da expressão*.

**Mais uma ressalva de vocabulário:** *tipo abstrato de dados* (TAD) é outra coisa, e está do lado dos **objetos**: esconde a representação atrás de uma interface (Aula 19).


## Bloco 6 — Tabela de síntese e ponte (≈ 5 min)

### Atualização da tabela (`tabela-design.md`)

| Linguagem | Avaliação | Vinculação | Escopo | Abstração | Estado | Dados | Controle | Tipos |
|---|---|---|---|---|---|---|---|---|
| `aljabr` v3 | estrita, exceto `if` | `let`, `letrec` | léxico | funções recursivas | — | números + closures | `if`, recursão | dinâmicos |
| `aljabr` v4 | estrita, exceto `if` e `match` (só o ramo escolhido) | `let`, `letrec`, variáveis de padrão (só no ramo) | léxico | funções recursivas | — | números + closures + **valores etiquetados (soma + produto)** | `if`, `match`, recursão | dinâmicos (o nome do tipo é só documentação) |
| `algora` v2 | estrita, exceto `if`/`while` | `var`, `def` | léxico (sobre locais) | closures, procedimentos | **store mutável** | números + closures | `if` (exp), `while` (cmd), blocos | dinâmicos |

Observe: `aljabr` v4 e `algora` partem da **mesma** v3 e variam **independentemente** em Estado e em Dados. Esse é exatamente o ponto da Unidade 9: dimensões de design independentes, e não categorias fixas. (Python, Scala e Rust combinam estado **e** tipos algébricos **e** objetos.)

### Ponte para a Aula 18

`algora` seguirá o Caminho 2: **classes e objetos**, aproveitando o store e os ambientes da Unidade 5. Dizer, ao final, que `aljabr` v4 volta como **referência de comparação** nas Aulas 18 e 19 (mesma AST, escrita nas duas linguagens).


## Tarefa prática (opcional): implementar `aljabr` v4

Mesmo formato da Aula 14 (§5.5).

| Especificação | Implementação |
|---|---|
| `CONSTR`, `PIPE`, `LBRACE`, `RBRACE`; `type`, `match` e `_` reservadas | novos tipos de token; `_` consultado no mapa de reservadas antes de virar `NOME` |
| `programa ::= { tipo_decl } exp` | `parse_programa` lê as declarações e preenche $\Delta$ (nome → aridade); construtor repetido é erro |
| `atomo` com `CONSTR [ ( args ) ]` | `parse_atomo`: após `CONSTR`, se o próximo token é `LPAREN`, lê os argumentos |
| `padrao`, `ramo`, `match` | `parse_padrao`, `parse_ramo`, `parse_match`; rejeitar variável repetida no padrão |
| (Cons), (ConsInvalido) | `eval` consulta $\Delta$ **antes** de avaliar os argumentos |
| `casa(p, v)` | função auxiliar que devolve um dicionário ou `None` |
| (Match), (MatchNenhum) | `eval` avalia o alvo, tenta os ramos em ordem, e só então estende o ambiente |
| (IfCond) ajustado | `if` com condição que não é número devolve `Erro` |

Conjunto de testes:

| Programa | Resultado |
|---|---|
| `type Lista = Vazia \| Cons(h, t)`<br>`letrec tamanho = fn (xs) => match xs { Vazia => 0  Cons(_, r) => 1 + tamanho(r) } in tamanho(Cons(1, Cons(2, Vazia)))` | `2` |
| `type Expr = Num(n) \| Add(a, b) \| Mul(a, b)`<br>`match Add(Num(2), Num(3)) { Num(n) => n  Add(a, b) => b }` | `Num(3)` |
| (mesmo `type`) `simplifica(Add(Num(0), Num(7)))`, com o programa do Bloco 3.2 | `Num(7)` |
| `match 5 { 0 => 1  _ => 2 }` | `2` |
| `match (fn (x) => x) { Num(n) => n  _ => 0 }` (com `Num` declarado) | `0` |
| `match Vazia { Cons(a, b) => a }` (com `Lista` declarado) | `erro` (MatchNenhum) |
| `Num(1, 2)` (com `Num/1`) | `erro` (ConsInvalido: aridade) |
| `Foo(1)` | `erro` (ConsInvalido: não declarado) |
| `Cons` (sem parênteses, com `Cons/2`) | `erro` (ConsInvalido) |
| `Num(2) + 1` | `erro` (*lift*) |
| `if Num(1) then 1 else 2` | `erro` (IfCond) |

E os programas abaixo devem ser **rejeitados pelo parser**: `Num()`, `match x { }`, `match x { Add(a, a) => a }`, `type T = A \| A`, `type T = vazia`, `let _ = 1 in 2`.


## Exercícios de fixação (sem entrega)

1. Em Python, escreva `soma(xs)` (soma dos elementos de uma `Lista`) usando `match`. Depois, escreva o mesmo em `aljabr` v4.
2. Estenda `simplifica` (Bloco 3.2) com a regra `Add(x, Num(0)) → x`. A ordem dos ramos importa? Dê um exemplo de entrada para o qual a ordem muda o resultado.
3. Derive, com as regras (Cons), (Match) e `casa`, o valor de
   `match Add(Num(1), Num(0)) { Add(Num(0), x) => x  Add(a, b) => b }`.
4. Retire o ramo `Mul` de `avalia` (Python). O que `avalia(Mul(Num(2), Num(3)))` devolve? Que decisão de design (MatchNenhum) `aljabr` v4 tomou de outro modo?
5. *(Reflexão)* Em Python, `case Num:` captura qualquer valor e não testa a classe. Que decisão de design do Bloco 4.1 evita esse problema em `aljabr` v4? Que preço ela cobra (pense em nomes de variáveis e no léxico)?
6. *(Reflexão)* No Bloco 4.3, mostramos que `if c then a else b` quase equivale a `match c { 0 => b  _ => a }`. Dê uma entrada para a qual eles **diferem**. Isso faz de `if` açúcar sintático de `match`?

