# Algora v2 → v3: o que mudou

Este arquivo lista **apenas as diferenças** entre Algora v2 (a que vocês já conhecem) e Algora v3 (records e objetos). Organizado por nível: léxico, sintático e semântica. Ao final, uma lista do que **não** mudou, e uma seção especial sobre uma **não-mudança importante**: `this` **não** é palavra reservada.

A ideia central da v3: **objetos = records + closures**, sem `class`, sem `new`, sem açúcar. Um record é um mapa `Nome ⇀ Val` que mora no store; um "método" é só um campo que contém uma closure. E nem `this` precisamos adicionar: o programador escolhe um nome (`this`, `self`, `obj`…) e closures capturam esse nome lexicalmente como qualquer variável.

---

## 1. Léxico

**Dois** terminais novos (e **nenhuma** palavra reservada nova).

| Terminal | Token | Papel |
|---|---|---|
| `:` | `COLON` | separador entre nome e expressão em record literal |
| `.` | `DOT` | acesso a campo (`e.n`) |

**Palavras reservadas (v3):** `var`, `def`, `fn`, `if`, `else`, `while` — **idênticas a v2**.

### Por que `:` e `.`?

- `:` só aparece em record literal (`{ x: 1 }`). É o token que **desambigua** `{` bloco × `{` record (ver §2).
- `.` é o operador de acesso a campo. Não é notação de OO: é acesso a record (como em Pascal/C). A notação de OO *emerge* de records + closures.

### O que **não** mudou no léxico

- `:=`, `var`, `def`, `fn`, `if`, `else`, `while`, `{`, `}`, `;`, `==`, `<`, `**`, `+`, `-`, `*`, `/`, `(`, `)`, `=`, `,`, `INTEIRO`, `NOME` — idênticos.
- Nenhuma palavra reservada nova. Em particular, **`this` não é palavra reservada** (ver §4).

---

## 2. Sintaxe

Quatro mudanças na EBNF. As duas primeiras são as importantes; as outras duas são consequências.

### 2.1 Nova produção: `record_lit`

```text
record_lit  ::= LBRACE [ campos ] RBRACE
campos      ::= campo { , campo }
campo       ::= NOME COLON exp
```

- `{}` vazio é o record vazio — o idioma para começar um objeto.
- `{ x: 1, y: 2 }` é um record com dois campos.
- Campos só têm nomes simples (`NOME`). Não há campos computados (`{ (e): v }` é inválido).
- **Ordem de avaliação dos campos é da esquerda para a direita.**

### 2.2 `chamada` reestruturada: `sufixo` unifica `.` e `()`

**v2:**
```text
chamada ::= atomo { LPAREN [ args ] RPAREN }
```

**v3:**
```text
chamada ::= atomo { sufixo }
sufixo  ::= DOT NOME                    ← NOVO (v3)
          | LPAREN [ args ] RPAREN
```

Por que essa mudança? Porque em v3 **duas coisas** são pós-fixadas: acesso a campo (`.n`) e aplicação (`(...)`). Unificando em `sufixo`, a gramática permite encadear livremente:

- `a.b`
- `f(x)`
- `a.b(c).d(e)`
- `f().x`

Consequência importante: **`obj.m(args)` e `(obj.m)(args)` são a mesma árvore sintática** — `.m` é um sufixo e `(args)` é outro. Não há "chamada de método" especial na gramática; é leitura de campo seguida de aplicação. Isso reflete o design: **não há despacho de método** na semântica.

### 2.3 Nova alternativa em `atribuicao`: atribuição a campo

**v2:**
```text
atribuicao ::= NOME := exp
```

**v3:**
```text
atribuicao ::= NOME := exp
             | chamada DOT NOME := exp        ← NOVO (v3): atribuição a campo
```

Exemplos válidos: `a.b := 5`, `obj.n := 0`, `f().x := 5`, `a.b.c := 5`.

Para o parser: reconhecer o padrão `chamada DOT NOME :=` e tratar o último `.NOME` como alvo.

### 2.4 `atomo` ganha `record_lit`

```text
atomo ::= INTEIRO | NOME | LPAREN exp RPAREN | bloco | record_lit
```

Apenas a alternativa `record_lit` é nova. `THIS` **não** aparece em `atomo` (não existe mais), nem `var_name` (não existe mais).

### 2.5 Desambiguação de `{`: bloco × record (contextual)

Esta é a mudança sintática que vocês precisam entender bem. Em v2, `{` era sempre bloco. Em v3, `{` pode ser bloco ou record literal, dependendo do contexto:

| Contexto | O que é `{` |
|---|---|
| **Posição de comando** (corpo de `while`, início de `bloco_cmd`) | **Bloco de comando** (sem expressão final) — como em v2 |
| **Posição de expressão**, conteúdo `{ }` | **Record vazio** (bloco vazio é inválido: exige expressão final) |
| **Posição de expressão**, conteúdo `{ NOME : ... }` | **Record literal** (o `:` é o discriminante) |
| **Posição de expressão**, qualquer outro conteúdo (`{ var ...`, `{ x ; ...`, `{ x + 1 }`, ...) | **Bloco-expressão** — como em v2 |

O parser precisa de **no máximo 1 token de lookahead** depois do primeiro `NOME` para decidir entre `NOME :` (record) e o resto (bloco). `{ }` vazio resolve sozinho.

**Consequência prática:** para retornar um record de uma função, use **chaves duplas** (o `{` externo é o corpo da função, o interno é o record):

```text
def ponto(x, y) { { x: x, y: y } }
```

É o mesmo fenômeno de JavaScript (`() => ({ x: 1 })`).

### O que **não** mudou na sintaxe

`programa`, `bloco`, `bloco_corpo`, `comando`, `while_cmd`, `bloco_cmd`, `func_decl`, `var_decl` (exceto o não-terminal do nome), `params`, `args`, e toda a hierarquia de operadores (`exp`, `comp`, `soma`, `termo`, `fator`, `unario`) permanecem **idênticas** a v2.

---

## 3. Semântica

Duas mudanças estruturais (domínios) e cinco regras novas (mais variantes de erro). O **julgamento semântico não muda**: continua `⟨e, ρ, σ⟩ ⇓ ⟨v, σ'⟩`. A novidade está nas regras, não na forma do julgamento.

### 3.1 Domínios: novo conjunto `Rec` e store estendido

**Novo domínio:**

$$\mathrm{Rec} = \mathrm{Nome} \rightharpoonup \mathrm{Val}$$

Um mapa de nomes de campo para valores.

**Store muda:**

| | v2 | v3 |
|---|---|---|
| Store | $\mathrm{Loc} \rightharpoonup \mathrm{Val}$ | $\mathrm{Loc} \rightharpoonup (\mathrm{Val} \cup \mathrm{Rec})$ |

**`Val` continua sem `Rec`.** Isso é deliberado. O invariante é:

> Uma localização criada por `RecordLit`/`NewRecord` armazena um $\mathrm{Rec}$; uma localização criada por `VarDecl`, `FunDecl` ou ligação de parâmetros armazena um $\mathrm{Val}$.

Por que isso importa? Porque **records são localizações, não valores**. Um record não "flutua" como valor: ele mora no store. É exatamente a separação $\rho/\sigma$ da Unidade 5 aplicada a agregados. Consequências:

- **Aliasing automático.** `var a := d1` copia a **localização**, não o mapa. Duas variáveis que apontam para o mesmo record veem as mesmas mutações.
- **`Var` continua simples.** Como `Val` não inclui `Rec`, a regra `Var` de v2 não muda: ela só pode retornar um valor escalar (número, closure, localização de record, erro).
- **`FieldRead`/`FieldWrite` exigem $\sigma(\ell) \in \mathrm{Rec}$.** Se a localização contém um número ou closure, é erro.

### 3.2 Cinco regras novas

#### (NewRecord) — `{}` vazio

$$\frac{\ell \notin \mathrm{dom}(\sigma)}{\langle \{\}, \rho, \sigma \rangle \Downarrow \langle \ell,\, \sigma[\ell \mapsto \varnothing] \rangle}$$

Aloca uma localização fresca com mapa vazio. É o "construtor" idiomático: comece com `{}`, adicione campos com `:=`.

#### (RecordLit) — `{ k₁:e₁, ..., kₙ:eₙ }`

Avalia os campos da esquerda para a direita, aloca uma localização fresca e preenche com o mapa.

$$\frac{\langle e_1,\dots,e_n \rangle \Downarrow \langle v_1,\dots,v_n \rangle \quad \ell \notin \mathrm{dom}(\sigma_n) \quad M = \{k_1 \mapsto v_1, \dots, k_n \mapsto v_n\}}{\langle \{k_1{:}e_1,\dots,k_n{:}e_n\}, \rho, \sigma_0 \rangle \Downarrow \langle \ell,\, \sigma_n[\ell \mapsto M] \rangle}$$

Detalhes:

- **Campos duplicados:** a especificação adota "último vence", mas recomenda-se rejeitar duplicatas na análise sintática.
- **Ordem:** esquerda para a direita, mesmo que o mapa não preserve ordem.
- **Equivalência:** avaliar os campos e depois alocar é equivalente a alocar primeiro (vazio) e preencher campo a campo via `FieldWrite`.

#### (FieldRead) — `e.n`

$$\frac{\langle e, \rho, \sigma_0 \rangle \Downarrow \langle \ell, \sigma_1 \rangle \quad \sigma_1(\ell) = M \quad M \in \mathrm{Rec} \quad M(n) = v}{\langle e.n, \rho, \sigma_0 \rangle \Downarrow \langle v, \sigma_1 \rangle}$$

Três variantes de erro:

- **`FieldReadNaoLoc`:** `e` não avalia para localização (ex.: `(5).n`).
- **`FieldReadNaoRec`:** a localização não contém record (ex.: `var x := 5; x.n`).
- **`FieldReadAusente`:** o campo `n` não existe no mapa. **Ler campo inexistente é erro** (não retorna "undefined").

**Nota crucial:** `e.n` **não** é lookup de variável. É leitura no store via localização. `obj.n` é `FieldRead(obj, n)`, e `obj` é resolvido por `Var` como qualquer variável. **Não há binding especial** (porque não há `this`).

#### (FieldWrite) — `e.n := e_rhs`

Avalia `e` para obter uma localização $\ell$, exige que $\sigma_1(\ell)$ seja um record, avalia $e_{\text{rhs}}$, **relê** o mapa em $\sigma_2(\ell)$ (o lado direito pode ter alterado o record por aliasing) e atualiza:

$$\frac{\langle e \rangle \Downarrow \langle \ell, \sigma_1 \rangle \quad \sigma_1(\ell) \in \mathrm{Rec} \quad \langle e_{\text{rhs}} \rangle \Downarrow \langle v, \sigma_2 \rangle \quad \sigma_2(\ell) = M \quad M' = M[n \mapsto v]}{\langle e.n := e_{\text{rhs}};\, \rho, \sigma_0 \rangle \Downarrow \langle \rho,\, \sigma_2[\ell \mapsto M'] \rangle}$$

Duas variantes de erro:

- **`FieldWriteNaoLoc`:** `e` não avalia para localização.
- **`FieldWriteNaoRec`:** a localização não contém record.

**Adição dinâmica de campo.** $M' = M[n \mapsto v]$ **insere** $n$ se não existe, ou atualiza se existe. Atribuir a campo inexistente **não é erro** — o campo é criado. É o estilo JavaScript, não OCaml.

**Ordem de avaliação:** `e` antes de $e_{\text{rhs}}$. Se `e` falhar, $e_{\text{rhs}}$ não é avaliada.

**Releitura do mapa:** depois de avaliar $e_{\text{rhs}}$, usamos $\sigma_2(\ell)$, não $\sigma_1(\ell)$, porque o lado direito pode ter chamado uma função que escreve no mesmo record (por aliasing).

#### (App) para `(obj.m)(args)`

**Nenhuma regra nova.** `obj.m` é `FieldRead(obj, m)`; se o campo contém uma closure, `App` de v2 se aplica. **Não há regra de despacho de método.** Esse é o coração do design: chamada de método é derivada de leitura de campo + aplicação.

### 3.3 Regras de v2 que **não** mudam

**Todas** as regras de v2 permanecem idênticas: `VarDecl`, `Assign`, `AssignNaoDeclarada`, `FunDecl`, `ExprStmt`, `Block`, `Num`, `Var`, `VarNaoLigada`, `Lam`, `App`, `AppNaoFuncao`, `AppAridade`, `IfVerd`, `IfFalso`, `IfCondFuncao`, `OpBinario`, `BlocoCmd`, `WhileFalso`, `WhileVerd`, `WhileCondFuncao`.

A convenção monádica de erros (§3.5) continua valendo. O julgamento $\langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma' \rangle$ **não muda**.

---

## 4. A não-mudança mais importante: `this` **não** é palavra reservada

Vocês podem esperar que, ao introduzir objetos, a linguagem ganhe uma palavra `this` com binding implícito (como Java) ou um `self` (como Python). **Não é o caso.**

Algora v3 **não** tem `this` como keyword. `this` é um `NOME` comum. Se o programador quiser usá-lo para nomear o record corrente, ótimo — mas também pode usar `self`, `me`, `obj`, `it`, ou qualquer outro nome.

Por que essa decisão?

1. **`this` não precisa de semântica especial.** Closures já capturam qualquer variável lexicalmente. Records já são mapas. Não há despacho de método.
2. **Adicionar `this` como keyword exigiria tratá-lo como caso especial** em declarações, atribuições e parâmetros — regras que **não ensinam nada** sobre o modelo.
3. **A convenção "use `this` para o objeto corrente" é do programador**, não da linguagem. (Em Python, `self` é exatamente isso: convenção, não keyword.)
4. **A ausência de keyword elimina a necessidade de binding implícito**, de regra especial e de um não-terminal a mais na gramática — sem perda de expressividade.

Construtor idiomático com `this`:

```text
def Contador() {
  var this := {};                       // nome escolhido pelo programador
  this.n := 0;
  this.inc := fn () { this.n := this.n + 1; this.n };
  this
}
```

O mesmo com `self`:

```text
def Contador() {
  var self := {};
  self.n := 0;
  self.inc := fn () { self.n := self.n + 1; self.n };
  self
}
```

**Moral:** objetos = records + closures + açúcar zero. Nem keyword precisamos adicionar.

---

## 5. Resumo: o que os alunos devem levar para casa

### Léxico
- `:` e `.` são tokens novos. **Nenhuma palavra reservada nova** — em particular, `this` **não** é keyword.

### Sintaxe
- `record_lit` novo: `{ k: e, ... }`, incluindo `{}`.
- `chamada` ganhou `sufixo`, que unifica `.` e `()`: `(obj.m)(args)` e `obj.m(args)` são a mesma árvore.
- Atribuição a campo: `chamada DOT NOME := exp`.
- `{` desambigua bloco × record contextualmente: `{}` = record vazio; `{ k: ... }` = record; resto = bloco.

### Semântica
- Novo domínio `Rec`; store armazena `Val ∪ Rec`; `Val` **não** inclui `Rec`.
- Records são **localizações**, não valores → aliasing automático.
- Três regras de expressão/comando novas: `RecordLit`/`NewRecord`, `FieldRead`, `FieldWrite` (com 5 variantes de erro).
- **Sem regra de despacho:** chamada de método é `FieldRead` + `App`.
- **Sem `this` implícito:** `this` (se usado) é capturado lexicalmente como qualquer variável.
- **Sem `class`, sem `new`, sem açúcar.**

### Frase de fechamento
> Objetos em Algora v3 são **records + closures + açúcar zero**. Um construtor é só uma função que cria `{}`, equipa com campos (inclusive métodos, que são closures) e devolve o record. **Nem `this` precisamos adicionar** — o programador escolhe um nome e closures capturam lexicalmente. E `obj.m(args)` é literalmente `(obj.m)(args)` — leitura de campo seguida de aplicação.