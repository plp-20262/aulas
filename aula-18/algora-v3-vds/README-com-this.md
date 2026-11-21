# Especificação de `algora` (v3) (vDS)

A linguagem **Algora** aqui especificada estende Algora v2 com **records** (objetos), construídos sobre records + closures, sem `class`, sem `new` e sem nenhum açúcar sintático. A v3 acrescenta:

- literais de record `{ k: e, ... }`, incluindo `{}` vazio;
- acesso a campo `e.n` (dot);
- atribuição a campo `e.n := e`;
- a palavra reservada `this`, que é uma variável comum (sem binding especial, sem semântica especial).

Records são **localizações no store**: um record é um mapa `Nome ⇀ Val` armazenado em um endereço. `var a := d1` copia a localização (aliasing automático). Adição dinâmica de campo é permitida (`this.n := 0` insere se não existe). Chamada de método é derivada: `(obj.m)(args)` = leitura de campo + aplicação.

> Este documento é a especificação formal da linguagem. O [Manual de Algora](MANUAL.md) descreve o uso da linguagem.

## Versões

| Versão | Mudanças |
|---|---|
| v1 | Versão base: estado e mutação (`var`, `:=`), declaração de funções (`def`), lambdas (`fn`), expressão condicional (`if`) e blocos `{ ... }` com retorno implícito. |
| v2 | Acrescenta o comando de repetição `while`. |
| v3 | Acrescenta records (objetos): literais `{ k: e, ... }`, acesso a campo `e.n`, atribuição a campo `e.n := e`, e a palavra reservada `this`. |

A v3 apenas acrescenta: nenhuma regra da v2 muda (a convenção de erros da §3.5 passa a cobrir também as novas relações). Nas seções abaixo, `← NOVO (v3)` marca o que foi introduzido na v3.

## 1. Léxico

A v3 introduz três novos terminais: `:` (separador de campo em record), `.` (acesso a campo) e `this` (palavra reservada).

```text
COLON     ::=  :              ← NOVO (v3)
DOT       ::=  \.             ← NOVO (v3)
THIS      ::=  this           ← NOVO (v3) (palavra reservada)

ASSIGN    ::=  :=
VAR       ::=  var
FUNCTION  ::=  def
FN        ::=  fn
IF        ::=  if
ELSE      ::=  else
WHILE     ::=  while
LBRACE    ::=  \{
RBRACE    ::=  \}
SEMICOLON ::=  ;
EQEQ      ::=  ==
LT        ::=  <
POW       ::=  \*\*
ADD       ::=  \+
SUB       ::=  -
MULT      ::=  \*
DIV       ::=  /
LPAREN    ::=  \(
RPAREN    ::=  \)
EQUAL     ::=  =
COMMA     ::=  ,
INTEIRO   ::=  [0-9]+
NOME      ::=  [a-zA-Z_][a-zA-Z0-9_]*  (exceto palavras reservadas)
```

**Palavras reservadas:** `var`, `def`, `fn`, `if`, `else`, `while`, `this`.

> **Nota para o Lexer:** `:=` deve vir antes de `=`, `**` antes de `*`, `==` antes de `=`. `this` é reservada: não pode ser usada como `NOME`. Ela pode, contudo, aparecer como variável em declarações, atribuições e parâmetros (ver §2).

## 2. Sintaxe (EBNF)

Um programa em Algora é um **bloco**: uma sequência de zero ou mais comandos seguidos de uma expressão final, cujo valor é o resultado da avaliação.

```text
programa    ::= bloco_corpo

bloco       ::= LBRACE bloco_corpo RBRACE
bloco_corpo ::= { comando } exp

comando     ::= func_decl
              | var_decl ;
              | atribuicao ;
              | while_cmd
              | exp ;

var_decl    ::= var var_name := exp
atribuicao  ::= var_name := exp
              | chamada DOT NOME := exp            ← NOVO (v3)
func_decl   ::= def NOME LPAREN [ params ] RPAREN bloco
while_cmd   ::= while exp bloco_cmd
bloco_cmd   ::= LBRACE { comando } RBRACE

var_name    ::= NOME | THIS                        ← NOVO (v3)
params      ::= var_name { , var_name }            ← NOVO (v3): `this` pode ser parâmetro

exp         ::= if exp bloco else bloco
              | fn LPAREN [ params ] RPAREN bloco
              | comp

comp        ::= soma [ ( == | < ) soma ]
soma        ::= termo { ( + | - ) termo }
termo       ::= fator { ( * | / ) fator }
fator       ::= unario [ ** fator ]
unario      ::= [ + | - ] chamada
chamada     ::= atomo { sufixo }
sufixo      ::= DOT NOME                           ← NOVO (v3)
              | LPAREN [ args ] RPAREN
atomo       ::= INTEIRO | NOME | THIS              ← NOVO (v3): THIS
              | LPAREN exp RPAREN
              | bloco
              | record_lit                         ← NOVO (v3)

record_lit  ::= LBRACE [ campos ] RBRACE           ← NOVO (v3)
campos      ::= campo { , campo }
campo       ::= NOME COLON exp

args        ::= exp { , exp }
```

### 2.1 Notas sobre a sintaxe

**`chamada` unifica acesso a campo e aplicação.** Em vez de `posfix` + `chamada` separados (como em v2), a v3 usa `chamada ::= atomo { sufixo }` com `sufixo ::= DOT NOME | LPAREN [args] RPAREN`. Isso permite encadear livremente: `a.b`, `f(x)`, `a.b(c).d(e)`, `f().x`, etc. A forma canônica de chamada de método é `(obj.m)(args)`, que a gramática produz naturalmente: `obj.m` é uma `chamada` (leitura de campo), seguida de `(args)`.

**Desambiguação de `{` (bloco × record).** `{` aparece em três contextos:

1. **Posição de comando** (corpo de `while`, início de `bloco_cmd`): `{` inicia um `bloco_cmd` (comandos, sem expressão final). Não há ambiguidade.
2. **Posição de expressão, como `atomo`**: `{` pode iniciar um `bloco` (expressão com retorno implícito) ou um `record_lit`. A desambiguação é contextual:
   - `{ }` → `record_lit` vazio (um `bloco` vazio não é válido, pois exige expressão final).
   - `{ NOME : ...` → `record_lit` (o `:` após o primeiro `NOME` é o discriminante).
   - Caso contrário (`{ var ...`, `{ def ...`, `{ while ...`, `{ NOME ; ...`, `{ exp ...`, etc.) → `bloco`.
   - O parser precisa de no máximo um token de lookahead além do primeiro token após `{` para decidir entre `NOME :` e o resto (LL(1) com um token de lookahead no ponto de decisão).
3. **Posição de expressão, como `exp`**: um `record_lit` em posição de expressão é um `atomo` (via `chamada`). Um `bloco` também é um `atomo`. A desambiguação é a mesma do item 2.

**`this` em declarações e atribuições.** `this` é reservada, mas pode ser usada como variável em `var this := exp`, `this := exp` e como parâmetro (`params`). Ela **não** pode ser usada como nome de função (`def this(...)` é inválido), nem como nome de campo (`{ this: 1 }` e `e.this` são inválidos), nem como `NOME` comum.

**Atribuição a campo.** `chamada DOT NOME := exp` permite atribuir a um campo de qualquer expressão que denote um record: `a.b := 5`, `this.n := 0`, `f().x := 5`, `a.b.c := 5` (aqui `chamada = a.b`, `DOT NOME = .c`). A forma `var_name := exp` cobre a atribuição a variável comum (`a := 5`, `this := {}`).

> **Nota de parsing para atribuição.** O parser deve reconhecer o padrão `chamada DOT NOME :=`. Na prática: parseie a `chamada` e, se o próximo token for `:=`, trate o último sufixo `.NOME` como alvo; caso contrário, o último sufixo `.NOME` pertence à `chamada` (e não há atribuição a campo).

**Record literal como valor de retorno.** O corpo de função é um `bloco` (bloco-expressão), então `fn (x) { { y: x } }` retorna um record (o `{` externo é o bloco, o interno é o record). Para retornar um record de uma função, use chaves duplas — como em JavaScript, `() => ({ x: 1 })` vira `fn () { { x: 1 } }`.

## 3. Semântica Operacional (*Big-Step*)

### 3.1 Domínios Semânticos

| Domínio | Notação | Descrição |
|---|---|---|
| Reais | $ℝ$ | Os números reais. |
| Locais / Endereços | $\mathrm{Loc}$ | Conjunto infinito e enumerável de endereços de memória. |
| *Closures* | $\mathrm{Clo} = \mathrm{Var}^* \times \mathrm{Bloco} \times \mathrm{Env}$ | Tripla: (parâmetros, bloco do corpo, ambiente de criação). |
| Records | $\mathrm{Rec} = \mathrm{Nome} \rightharpoonup \mathrm{Val}$ | Mapeamento parcial de nomes de campo para valores. |
| Valores | $\mathrm{Val} = ℝ \cup \mathrm{Clo} \cup \mathrm{Loc} \cup \{ \mathbf{erro} \}$ | Valores denotáveis. |
| Ambientes | $\mathrm{Env} = \mathrm{Var} \rightharpoonup \mathrm{Loc}$ | Mapeamento de nomes de variáveis para endereços. |
| Memória (*Store*) | $\mathrm{Store} = \mathrm{Loc} \rightharpoonup (\mathrm{Val} \cup \mathrm{Rec})$ | Mapeamento parcial de endereços para valores ou records. |

> **Invariante de store.** Uma localização criada por `RecordLit` (ou `NewRecord`) armazena um $\mathrm{Rec}$; uma localização criada por `VarDecl`, `FunDecl` ou pela ligação de parâmetros em `App` armazena um $\mathrm{Val}$. Assim, $\mathrm{Rec}$ nunca é o resultado direto de uma expressão: expressões retornam $\mathrm{Val}$. Isso simplifica as regras: `Var` pode assumir $\sigma(\ell) \in \mathrm{Val}$; `FieldRead`/`FieldWrite` exigem $\sigma(\ell) \in \mathrm{Rec}$.

### 3.2 Framework semântico

A semântica opera sob um modelo de memória de dois níveis ($\rho, \sigma$), como em v2:

1. **Comandos:** $\langle c, \rho, \sigma \rangle \Downarrow \langle \rho_1, \sigma_1 \rangle$
2. **Expressões e blocos:** $\langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle$
3. **Corpo de laço:** $\langle b, \rho, \sigma \rangle \Downarrow_s \sigma_1$

O julgamento semântico **não muda** em relação a v2: $\langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma' \rangle$. A novidade está nas regras, não nos domínios (exceto pela adição de $\mathrm{Rec}$ ao store).

### 3.3 Regras de Avaliação de Comandos

#### Declaração de Variável (`var`)

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle \qquad \ell \notin \mathrm{dom}(\sigma_1)
}{
  \langle \mathtt{var}\ x\ \mathtt{:=}\ e;\, \rho, \sigma \rangle \Downarrow \langle \rho[x \mapsto \ell],\, \sigma_1[\ell \mapsto v] \rangle
} \quad \text{(VarDecl)}
$$

#### Atribuição a variável (`:=`)

$$
\frac{
  \rho(x) = \ell \qquad \langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle
}{
  \langle x\ \mathtt{:=}\ e;\, \rho, \sigma \rangle \Downarrow \langle \rho,\, \sigma_1[\ell \mapsto v] \rangle
} \quad \text{(Assign)}
$$

$$
\frac{
  x \notin \mathrm{dom}(\rho)
}{
  \langle x\ \mathtt{:=}\ e;\, \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(AssignNaoDeclarada)}
$$

#### Atribuição a campo (`e.n := e_rhs`) ← NOVO (v3)

Avalia a expressão base $e$ para obter uma localização $\ell$; exige que $\sigma_1(\ell)$ seja um record; avalia o lado direito; relê o mapa em $\sigma_2(\ell)$ (o lado direito pode ter alterado o record por aliasing); e atualiza o mapa, **inserindo** o campo se ele não existir:

$$
\frac{
  \begin{matrix}
  \langle e, \rho, \sigma_0 \rangle \Downarrow \langle \ell, \sigma_1 \rangle \qquad
  \sigma_1(\ell) \in \mathrm{Rec} \\
  \langle e_{\text{rhs}}, \rho, \sigma_1 \rangle \Downarrow \langle v, \sigma_2 \rangle \qquad
  \sigma_2(\ell) = M \qquad M \in \mathrm{Rec} \qquad M' = M[n \mapsto v]
  \end{matrix}
}{
  \langle e.n\ \mathtt{:=}\ e_{\text{rhs}};\, \rho, \sigma_0 \rangle \Downarrow \langle \rho,\, \sigma_2[\ell \mapsto M'] \rangle
} \quad \text{(FieldWrite)}
$$

Erros:

$$
\frac{
  \langle e, \rho, \sigma_0 \rangle \Downarrow \langle v, \sigma_1 \rangle \qquad v \notin \mathrm{Loc}
}{
  \langle e.n\ \mathtt{:=}\ e_{\text{rhs}};\, \rho, \sigma_0 \rangle \Downarrow \mathbf{erro}
} \quad \text{(FieldWriteNaoLoc)}
$$

$$
\frac{
  \langle e, \rho, \sigma_0 \rangle \Downarrow \langle \ell, \sigma_1 \rangle \qquad \sigma_1(\ell) \notin \mathrm{Rec}
}{
  \langle e.n\ \mathtt{:=}\ e_{\text{rhs}};\, \rho, \sigma_0 \rangle \Downarrow \mathbf{erro}
} \quad \text{(FieldWriteNaoRec)}
$$

Observações:

- **Ordem de avaliação.** $e$ é avaliada antes de $e_{\text{rhs}}$. Se $e$ falhar (não for localização ou não for record), $e_{\text{rhs}}$ **não** é avaliada.
- **Releitura do mapa.** Como $e_{\text{rhs}}$ pode alterar o record por aliasing (por exemplo, chamando uma função que escreve no mesmo record), o mapa usado para a atualização é $\sigma_2(\ell)$, não $\sigma_1(\ell)$.
- **Adição dinâmica.** $M' = M[n \mapsto v]$ insere $n$ se não existir, ou atualiza se existir. Não é erro atribuir a um campo inexistente.
- **Ambiente.** O ambiente $\rho$ não muda.

#### Declaração de Função Nomeada (`def`)

$$
\frac{
  \ell_f \notin \mathrm{dom}(\sigma) \qquad \rho_1 = \rho[f \mapsto \ell_f] \qquad v_f = \mathsf{clo}((p_1, \ldots, p_n), e_{\text{corpo}}, \rho_1)
}{
  \langle \mathtt{def}\ f(p_1, \ldots, p_n)\ e_{\text{corpo}},\, \rho, \sigma \rangle \Downarrow \langle \rho_1,\, \sigma[\ell_f \mapsto v_f] \rangle
} \quad \text{(FunDecl)}
$$

#### Expressão como Comando (`exp ;`)

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle \qquad v \neq \mathbf{erro}
}{
  \langle e;\, \rho, \sigma \rangle \Downarrow \langle \rho, \sigma_1 \rangle
} \quad \text{(ExprStmt)}
$$

#### Laço (`while`)

$$
\frac{
  \langle c_1, \rho, \sigma_0 \rangle \Downarrow \langle \rho_1, \sigma_1 \rangle \quad \dots \quad \langle c_n, \rho_{n-1}, \sigma_{n-1} \rangle \Downarrow \langle \rho_n, \sigma_n \rangle
}{
  \langle \{ c_1 \dots c_n \}, \rho, \sigma_0 \rangle \Downarrow_s \sigma_n
} \quad \text{(BlocoCmd)}
$$

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle 0, \sigma_1 \rangle
}{
  \langle \mathtt{while}\ e\ b, \rho, \sigma \rangle \Downarrow \langle \rho, \sigma_1 \rangle
} \quad \text{(WhileFalso)}
$$

$$
\frac{
  \begin{matrix}
  \langle e, \rho, \sigma \rangle \Downarrow \langle n, \sigma_1 \rangle \quad (n \in ℝ,\ n \neq 0) \qquad
  \langle b, \rho, \sigma_1 \rangle \Downarrow_s \sigma_2 \\
  \langle \mathtt{while}\ e\ b, \rho, \sigma_2 \rangle \Downarrow \langle \rho, \sigma_3 \rangle
  \end{matrix}
}{
  \langle \mathtt{while}\ e\ b, \rho, \sigma \rangle \Downarrow \langle \rho, \sigma_3 \rangle
} \quad \text{(WhileVerd)}
$$

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle v_c, \sigma_1 \rangle \qquad v_c \in \mathrm{Clo}
}{
  \langle \mathtt{while}\ e\ b, \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(WhileCondFuncao)}
$$

### 3.4 Regras de Avaliação de Expressões e Blocos

#### Blocos e Retorno Implícito (`Block`)

$$
\frac{
  \begin{matrix}
  \langle c_1, \rho, \sigma_0 \rangle \Downarrow \langle \rho_1, \sigma_1 \rangle \quad \dots \quad \langle c_n, \rho_{n-1}, \sigma_{n-1} \rangle \Downarrow \langle \rho_n, \sigma_n \rangle \\
  \langle e_{\text{final}}, \rho_n, \sigma_n \rangle \Downarrow \langle v, \sigma_{n+1} \rangle
  \end{matrix}
}{
  \langle \{ c_1 \dots c_n\ e_{\text{final}} \}, \rho, \sigma_0 \rangle \Downarrow \langle v, \sigma_{n+1} \rangle
} \quad \text{(Block)}
$$

#### Números e Variáveis

$$
\frac{}{
  \langle n, \rho, \sigma \rangle \Downarrow \langle n, \sigma \rangle
} \quad \text{(Num)}
$$

$$
\frac{
  \rho(x) = \ell \qquad \sigma(\ell) = v
}{
  \langle x, \rho, \sigma \rangle \Downarrow \langle v, \sigma \rangle
} \quad \text{(Var)}
$$

$$
\frac{
  x \notin \mathrm{dom}(\rho)
}{
  \langle x, \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(VarNaoLigada)}
$$

#### Criação de Lambda Anônimo (`fn`)

$$
\frac{}{
  \langle \mathtt{fn}\ (p_1, \ldots, p_n)\ e_{\text{bloco}},\, \rho, \sigma \rangle \Downarrow \langle \mathsf{clo}((p_1, \ldots, p_n), e_{\text{bloco}}, \rho),\, \sigma \rangle
} \quad \text{(Lam)}
$$

#### Aplicação de Função (`Call`)

$$
\frac{
  \begin{matrix}
  \langle e_f, \rho, \sigma_0 \rangle \Downarrow \langle \mathsf{clo}((p_1, \ldots, p_n), e_{\text{corpo}}, \rho_0),\, \sigma_1 \rangle \\
  \langle a_1, \rho, \sigma_1 \rangle \Downarrow \langle v_1, \sigma_2 \rangle \quad \dots \quad \langle a_n, \rho, \sigma_n \rangle \Downarrow \langle v_n, \sigma_{n+1} \rangle \\
  \ell_1, \ldots, \ell_n \notin \mathrm{dom}(\sigma_{n+1}) \quad \text{(distintos)} \\
  \rho_1 = \rho_0[p_1 \mapsto \ell_1, \dots, p_n \mapsto \ell_n] \\
  \sigma'_1 = \sigma_{n+1}[\ell_1 \mapsto v_1, \dots, \ell_n \mapsto v_n] \\
  \langle e_{\text{corpo}}, \rho_1, \sigma'_1 \rangle \Downarrow \langle v, \sigma_{n+2} \rangle
  \end{matrix}
}{
  \langle e_f(a_1, \ldots, a_n), \rho, \sigma_0 \rangle \Downarrow \langle v, \sigma_{n+2} \rangle
} \quad \text{(App)}
$$

$$
\frac{
  \langle e_f, \rho, \sigma \rangle \Downarrow \langle v_f, \sigma_1 \rangle \qquad v_f \notin \mathrm{Clo}
}{
  \langle e_f(a_1, \ldots, a_m), \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(AppNaoFuncao)}
$$

$$
\frac{
  \langle e_f, \rho, \sigma \rangle \Downarrow \langle \mathsf{clo}((p_1, \ldots, p_n), e_b, \rho_0), \sigma_1 \rangle \qquad m \neq n
}{
  \langle e_f(a_1, \ldots, a_m), \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(AppAridade)}
$$

#### Expressão Condicional (`if`)

$$
\frac{
  \langle c, \rho, \sigma_0 \rangle \Downarrow \langle n, \sigma_1 \rangle \quad (n \in ℝ,\ n \neq 0) \qquad
  \langle b_{\text{then}}, \rho, \sigma_1 \rangle \Downarrow \langle v, \sigma_2 \rangle
}{
  \langle \mathtt{if}\ c\ b_{\text{then}}\ \mathtt{else}\ b_{\text{else}}, \rho, \sigma_0 \rangle \Downarrow \langle v, \sigma_2 \rangle
} \quad \text{(IfVerd)}
$$

$$
\frac{
  \langle c, \rho, \sigma_0 \rangle \Downarrow \langle 0, \sigma_1 \rangle \qquad
  \langle b_{\text{else}}, \rho, \sigma_1 \rangle \Downarrow \langle v, \sigma_2 \rangle
}{
  \langle \mathtt{if}\ c\ b_{\text{then}}\ \mathtt{else}\ b_{\text{else}}, \rho, \sigma_0 \rangle \Downarrow \langle v, \sigma_2 \rangle
} \quad \text{(IfFalso)}
$$

$$
\frac{
  \langle c, \rho, \sigma_0 \rangle \Downarrow \langle v_c, \sigma_1 \rangle \qquad v_c \in \mathrm{Clo}
}{
  \langle \mathtt{if}\ c\ b_{\text{then}}\ \mathtt{else}\ b_{\text{else}}, \rho, \sigma_0 \rangle \Downarrow \mathbf{erro}
} \quad \text{(IfCondFuncao)}
$$

#### Operadores

$$
\frac{
  \langle e_1, \rho, \sigma_0 \rangle \Downarrow \langle v_1, \sigma_1 \rangle \qquad
  \langle e_2, \rho, \sigma_1 \rangle \Downarrow \langle v_2, \sigma_2 \rangle
}{
  \langle e_1 \text{ op } e_2, \rho, \sigma_0 \rangle \Downarrow \langle f_{\mathrm{op}}^{\uparrow}(v_1, v_2), \sigma_2 \rangle
} \quad \text{(OpBinario)}
$$

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle \qquad v \in ℝ
}{
  \langle \text{op } e, \rho, \sigma \rangle \Downarrow \langle f_{\mathrm{op}}(v), \sigma_1 \rangle
} \quad \text{(Unario)}
$$

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle \qquad v \notin ℝ
}{
  \langle \text{op } e, \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(UnarioNaoNumero)}
$$

> Nota: `Unario`/`UnarioNaoNumero` esclarecem o comportamento dos sinais `+x` e `-x` descritos no manual da v2 (a especificação formal da v2 os omite). A v3 não os altera: `f_+ = \lambda v.v` e `f_- = \lambda v.-v`.

#### Literal de record (`{ k₁:e₁, ..., kₙ:eₙ }`) ← NOVO (v3)

Os campos são avaliados **da esquerda para a direita**. Depois, uma localização fresca $\ell$ é alocada e preenchida com o mapa:

$$
\frac{
  \begin{matrix}
  \langle e_1, \rho, \sigma_0 \rangle \Downarrow \langle v_1, \sigma_1 \rangle \quad \dots \quad
  \langle e_n, \rho, \sigma_{n-1} \rangle \Downarrow \langle v_n, \sigma_n \rangle \\
  \ell \notin \mathrm{dom}(\sigma_n) \qquad M = \{k_1 \mapsto v_1, \dots, k_n \mapsto v_n\}
  \end{matrix}
}{
  \langle \{ k_1{:}e_1, \dots, k_n{:}e_n \}, \rho, \sigma_0 \rangle \Downarrow
  \langle \ell,\, \sigma_n[\ell \mapsto M] \rangle
} \quad \text{(RecordLit)}
$$

Para $n = 0$ (record vazio), a regra é o caso particular:

$$
\frac{
  \ell \notin \mathrm{dom}(\sigma)
}{
  \langle \{ \}, \rho, \sigma \rangle \Downarrow \langle \ell,\, \sigma[\ell \mapsto \varnothing] \rangle
} \quad \text{(NewRecord)}
$$

Observações:

- **Avaliação antes da alocação.** Como $\ell$ é fresco e não é acessível durante a avaliação dos campos, avaliar os campos e alocar $\ell$ ao final é equivalente a alocar $\ell$ primeiro (com mapa vazio) e preencher campo a campo. A forma "alocar primeiro" corresponde a `NewRecord` seguido de `FieldWrite` para cada campo.
- **Campos duplicados.** A notação $\{k_1 \mapsto v_1, \dots\}$ com chaves repetidas é o mapa com a **última associação vencendo**. Uma implementação pode tratar campos duplicados como erro de elaboração; a especificação adota "último vence" por simplicidade, mas recomenda-se rejeitar duplicatas na análise sintática.
- **Ordem dos campos.** A ordem de avaliação é a ordem textual (esquerda para a direita), mesmo que o mapa resultante não preserve ordem.
- **Nomes de campo.** Apenas `NOME` (identificadores). Não há campos computados (`{ (e): v }` é inválido) nem `this` como nome de campo.

#### Leitura de campo (`e.n`) ← NOVO (v3)

$$
\frac{
  \langle e, \rho, \sigma_0 \rangle \Downarrow \langle \ell, \sigma_1 \rangle \qquad
  \sigma_1(\ell) = M \qquad M \in \mathrm{Rec} \qquad M(n) = v
}{
  \langle e.n, \rho, \sigma_0 \rangle \Downarrow \langle v, \sigma_1 \rangle
} \quad \text{(FieldRead)}
$$

$$
\frac{
  \langle e, \rho, \sigma_0 \rangle \Downarrow \langle v, \sigma_1 \rangle \qquad v \notin \mathrm{Loc}
}{
  \langle e.n, \rho, \sigma_0 \rangle \Downarrow \mathbf{erro}
} \quad \text{(FieldReadNaoLoc)}
$$

$$
\frac{
  \langle e, \rho, \sigma_0 \rangle \Downarrow \langle \ell, \sigma_1 \rangle \qquad \sigma_1(\ell) \notin \mathrm{Rec}
}{
  \langle e.n, \rho, \sigma_0 \rangle \Downarrow \mathbf{erro}
} \quad \text{(FieldReadNaoRec)}
$$

$$
\frac{
  \langle e, \rho, \sigma_0 \rangle \Downarrow \langle \ell, \sigma_1 \rangle \qquad
  \sigma_1(\ell) = M \qquad M \in \mathrm{Rec} \qquad n \notin \mathrm{dom}(M)
}{
  \langle e.n, \rho, \sigma_0 \rangle \Downarrow \mathbf{erro}
} \quad \text{(FieldReadAusente)}
$$

Observações:

- `e.n` **não** é um lookup de variável: é uma leitura no store via localização. A variável `this` não tem tratamento especial: `this.n` é `FieldRead(this, n)`, e `this` é resolvido por `Var` como qualquer variável.
- A regra `FieldRead` cobre `(obj.m)(args)`: `obj.m` é `FieldRead(obj, m)` (retorna a closure armazenada no campo `m`), e `App` aplica a closure aos argumentos. **Não há regra de despacho de método.**

### 3.5 Convenção Monádica de Propagação de Erros

Se qualquer premissa da forma $\langle e, \rho, \sigma \rangle \Downarrow \mathbf{erro}$, $\langle c, \rho, \sigma \rangle \Downarrow \mathbf{erro}$ ou $\langle b, \rho, \sigma \rangle \Downarrow_s \mathbf{erro}$ produzir $\mathbf{erro}$, a avaliação da regra é interrompida imediatamente e a conclusão de toda a derivação é $\mathbf{erro}$.

## 4. Notas de design

**Records são localizações, não valores.** Um record não é um valor "solto": é uma localização no store cujo conteúdo é um mapa. Isso reusa a separação $\rho/\sigma$ da Unidade 5 e explica o aliasing automaticamente: `var a := d1` copia a localização, não o mapa.

**Sem `class`, sem `new`, sem açúcar.** Um "método" é apenas um campo que contém uma closure. Um "construtor" é uma função que cria o record, equipa e devolve:

```text
def Contador() {
  var this := {};
  this.n := 0;
  this.inc := fn () { this.n := this.n + 1; this.n };
  this
}
```

Não há `this` implícito: `this` é uma variável comum (reservada), capturada lexicalmente pelas closures. O programador pode reatribuir `this` (responsabilidade dele).

**Chamada de método é derivada.** `(obj.m)(args)` = leitura de campo + aplicação. `obj.m(args)` é a mesma coisa, graças à gramática de `chamada` (o `.m` é um sufixo e `(args)` é outro). Não há regra de despacho.

**Encapsulamento não é imposto.** `d1.n` é acessível de fora. A discussão de encapsulamento (convenção × compilador × ausência de sintaxe × freeze) fica para a Aula 19.

**Adição dinâmica de campo.** `this.n := 0` insere `n` se não existe (estilo JS, não OCaml). Isso é consequência de `M' = M[n \mapsto v]` em `FieldWrite`.

**Blocos de expressão × blocos de comando.** A distinção de v2 é mantida: corpo de função e última expressão de bloco-expressão são posições de expressão; corpo de `while`, ramo de `if`-comando e início de bloco são posições de comando. `{` em posição de expressão é record (ou bloco, se o conteúdo não for `NOME :`); `{` em posição de comando é bloco de comando.

**`this` reservada, mas variável comum.** `this` pode ser declarada (`var this := {}`), atribuída (`this := {}`) e usada como parâmetro (`def f(this) { ... }`). Não pode ser nome de função, de campo ou `NOME` comum. Não há binding especial: closures capturam `this` lexicalmente.

## 5. Exemplo completo

```text
def Contador() {
  var this := {};
  this.n := 0;
  this.inc := fn () { this.n := this.n + 1; this.n };
  this
}

var c1 := Contador();
var c2 := Contador();
c1.inc();
c1.inc();
c2.inc();
c1.n + c2.n
```

Resultado: `3` (o `c1` tem `n = 2`, o `c2` tem `n = 1`; contadores independentes).
