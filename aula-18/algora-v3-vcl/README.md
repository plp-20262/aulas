# Especificação de `algora` (v3) (vCl)

A linguagem **Algora** aqui especificada estende a linguagem Aljabr com
construções imperativas e retorno implícito de expressões (estilo Rust). Ela
substitui as expressões `let` / `letrec` por comandos de declaração (`var`) e
atribuição mutável (`:=`); introduz também blocos delimitados por chaves `{ ...
}` com sub-escopo, em que a **última expressão** define o valor retornado pelo
bloco ou função.

A linguagem **Algora** pode ser vista como uma extensão de Aljabr (versão v3)
com construções típicas de linguagens imperativas. Para isso, a linguagem
adiciona suporte a _estado_ e _mutação_. O nome é proposto como uma fusão de
Aljabr e Algol, uma das representantes de maior relevância histórica dentre as
linguagens imperativas e de programação estruturada.

Na v3, Algora ganha também **registros** (`{ nome: exp, ... }`), valores
compostos e mutáveis, no estilo dos objetos literais de JavaScript. Nenhum
mecanismo de orientação a objetos é adicionado à linguagem: a combinação de
*closures* (já presentes desde Aljabr), registros e mutação (desde a v1) é
suficiente para escrever programas orientados a objetos (veja a seção
"Registros e objetos (v3)").

> Este documento é a especificação formal da linguagem, para fins de referência
> para a implementação de tradutores (sejam interpretadores e/ou compiladores).
> Você também pode ler o [Manual de Algora](MANUAL.md), para ver como as
> _features_ da linguagem podem ser usadas. Por fim, você também pode ver
> exemplos de pequenos programas no diretório [exemplos](exemplos).

## Versões

| Versão | Mudanças |
|---|---|
| v1 | Versão base: estado e mutação (`var`, `:=`), declaração de funções (`def`), lambdas (`fn`), expressão condicional (`if`) e blocos `{ ... }` com retorno implícito. |
| v2 | Acrescenta o comando de repetição `while`. |
| v3 | Acrescenta registros: literal `{ nome: exp, ... }`, acesso a campo `e.f` e atribuição a campo `e.f := exp`. |

A v2 apenas acrescenta: nenhuma regra da v1 muda (a convenção de erros da §3.5
só passa a cobrir também a nova relação $\Downarrow_s$). A v3 também apenas
acrescenta: todo programa válido na v2 continua válido na v3, com o mesmo
significado, e nenhuma regra da v1 ou da v2 muda. A única reorganização é
sintática: a produção `chamada` da gramática passa a se chamar `posfixo`, pois
agora também cobre o acesso a campo. A v3 não introduz novas relações
semânticas nem novas palavras reservadas; introduz dois novos símbolos léxicos
(`:` e `.`).

Nas seções abaixo, `← NOVO` marca o que é novo em relação a Aljabr, `← NOVO
(v2)` marca o que foi introduzido na v2 e `← NOVO (v3)` marca o que foi
introduzido na v3. Como consequência da v2, `while` passa a ser palavra
reservada e deixa de poder ser usado como nome.

## Características Aljabr

### Similaridade com Aljabr

As principais similaridades de Algora com Aljabr (que é uma linguagem funcional
pura) reside nos seguintes aspectos:

1. funções são cidadãs de primeira classe;
2. funções são lambdas e podem ser anônimas;
3. funções também podem ter nome e suportam recursividade (como `letrec`);
4. em nível semântico, funções são _closures_.

### Similaridades com Algol

Algora, contudo, também suporta construções imperativas, mais especificamente:

1. variáveis com estado (mutáveis);
2. comando de atribuição de variáveis;
3. comandos de declaração (de variáveis e de funções);
4. programas como sequências de comandos;
5. comando de repetição (`while`), a partir da v2.

### Registros e objetos (v3)

A v3 acrescenta **registros**: valores compostos por campos nomeados, como em
`{ x: 3, y: 4 }`. Três propriedades definem o seu papel na linguagem:

1. um registro é um valor de primeira classe: pode ser guardado em variáveis,
   passado como argumento, devolvido por funções e guardado em campos de outros
   registros;
2. um registro é **mutável** e tem **identidade**: ele vive na memória e é
   manipulado por *referência*. Atribuir um registro a outra variável, ou
   passá-lo a uma função, copia a referência, não o registro;
3. os campos de um registro podem conter qualquer valor, **inclusive funções**
   (closures).

Com isso, a **orientação a objetos básica** deixa de ser uma construção nova e
passa a ser uma *consequência* de elementos que a linguagem já tinha:

| Elemento | Origem | Papel na orientação a objetos |
|---|---|---|
| *closures* | Aljabr | os "métodos" lembram o ambiente onde foram criados, inclusive suas variáveis |
| mutação (`var`, `:=`) | v1 | o "estado" do objeto pode mudar com o tempo |
| registros | v3 | o "objeto": agrupa os métodos (e, opcionalmente, o estado) sob nomes |

Não há classes, herança, nem uma palavra como `this`/`self`. Também **não há
regra semântica própria para "invocar um método"**: `o.m(a)` é uma aplicação de
função comum (regra (App), §3.4) cuja função é o valor do campo `m` do registro
`o`. Um objeto que precisa se referenciar usa uma variável local (por convenção,
`este`) que aponta para o próprio registro. Exemplo:

```text
def Contador() {
    var este := {};
    este.n := 0;
    este.inc := fn() { este.n := este.n + 1; este.n };
    este.get := fn() { este.n };
    este
}
var c1 := Contador();
var c2 := Contador();
c1.inc();
c1.inc();
c2.inc();
c1.get() + 1000 * c2.get()       // 1002
```

Cada chamada de `Contador()` cria um novo registro e uma nova variável `este`;
por isso `c1` e `c2` são independentes.

### Sintaxe própria, diferente de Aljabr e Algol

As similaridades mencionadas acima são de naturez semântica, não sintática e
léxica. Nesse sentido, Aljabr usa um mix de elementos de diferentes linguagens
modernas. Para a atribuição, contudo, usarei o clássico símbolo `:=`
introduzido por Algol. Abaixo, seguem as especificações formais da linguagem.


## 1. Léxico

A linguagem **Algora** introduz novos delimitadores de bloco (`{`, `}`),
terminação de instrução (`;`), atribuição mutável (`:=`) e declaração de função
(`def`).

```text
ASSIGN    ::=  :=              ← NOVO
VAR       ::=  var             ← NOVO (palavra reservada)
FUNCTION  ::=  def             ← NOVO (palavra reservada)
FN        ::=  fn              (palavra reservada)
IF        ::=  if              (palavra reservada)
ELSE      ::=  else            (palavra reservada)
WHILE     ::=  while           ← NOVO (v2) (palavra reservada)
LBRACE    ::=  \{              ← NOVO
RBRACE    ::=  \}              ← NOVO
SEMICOLON ::=  ;               ← NOVO
COLON     ::=  :               ← NOVO (v3)
DOT       ::=  \.              ← NOVO (v3)
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

**Palavras reservadas:** `var`, `def`, `fn`, `if`, `else`, `while`.

> **Nota para o Lexer:** `:=` (`ASSIGN`) deve vir antes de `=` (`EQUAL`), assim
> como `**` vem antes de `*` e `==` vem antes de `=`. Na v3, `:=` (`ASSIGN`)
> também deve vir antes de `:` (`COLON`): `x:=1` é `NOME ASSIGN INTEIRO`, mas
> `x: 1` é `NOME COLON INTEIRO`. Identificadores da categoria `NOME` aceitam
> letras maiúsculas e minúsculas. Como `INTEIRO` não contém ponto, o símbolo `.`
> é sempre o `DOT` do acesso a campo.


## 2. Sintaxe (EBNF)

Um programa em **Algora** é estruturado como um **bloco**: uma sequência de
zero ou mais comandos (*statements*) seguidos de um `;` (ponto e vírgula),
finalizada por uma expressão cujo valor será tomado como o resultado da
avaliação do programa. Esta decisão vincula a linguagem à semântica de Aljabr,
porque faz todo programa e todo corpo de bloco (veja abaixo) ter um valor
associado (o da última expressão que o forma).

```text
programa    ::= bloco_corpo

bloco       ::= LBRACE bloco_corpo RBRACE
bloco_corpo ::= { comando } exp

comando     ::= func_decl
              | var_decl ;
              | atribuicao ;
              | while_cmd         ← NOVO (v2) (não é seguido de ";")
              | exp ;             ← (exp seguido de ";" é um comando)

var_decl    ::= var NOME := exp
atribuicao  ::= NOME := exp
              | acesso := exp                          ← NOVO (v3)
func_decl   ::= def NOME LPAREN [ params ] RPAREN bloco
while_cmd   ::= while exp bloco_cmd                    ← NOVO (v2)
bloco_cmd   ::= LBRACE { comando } RBRACE              ← NOVO (v2)

exp         ::= if exp bloco else bloco
              | fn LPAREN [ params ] RPAREN bloco
              | comp

comp        ::= soma [ ( == | < ) soma ]
soma        ::= termo { ( + | - ) termo }
termo       ::= fator { ( * | / ) fator }
fator       ::= unario [ ** fator ]
unario      ::= [ + | - ] posfixo                      ← (v3) antes: chamada
posfixo     ::= atomo { sufixo }                       ← (v3) antes: chamada
sufixo      ::= LPAREN [ args ] RPAREN                 (chamada)
              | . NOME                                 ← NOVO (v3) (acesso a campo)
acesso      ::= atomo { sufixo } . NOME                ← NOVO (v3)
atomo       ::= INTEIRO | NOME | LPAREN exp RPAREN | bloco
              | registro                               ← NOVO (v3)

registro    ::= LBRACE [ campo { , campo } ] RBRACE    ← NOVO (v3)
campo       ::= NOME : exp                             ← NOVO (v3)

params      ::= NOME { , NOME }
args        ::= exp { , exp }
```

Sobre o comando `while` (v2):

- `while e b` repete o corpo `b` enquanto a condição `e` for verdadeira (a
  semântica está na §3.3).
- Um `while_cmd` é um **comando**, não uma expressão: não produz valor e não
  pode aparecer onde se espera uma `exp` (por exemplo, `var x := while ...` é
  inválido). Como `func_decl`, não é seguido de `;`.
- O corpo é um `bloco_cmd`: uma sequência de zero ou mais comandos **sem
  expressão final**. Toda expressão no corpo precisa, portanto, ser seguida de
  `;` (é um `exp ;`), e o corpo não tem valor.
- Por não ter valor, um `while_cmd` não pode ser a última coisa de um
  `bloco_corpo`: ele precisa ser seguido pela expressão final do bloco.
- Não há ambiguidade entre a condição e o corpo: depois de uma expressão
  completa, um `{` não pode continuar a expressão (ele só inicia um bloco quando
  aparece no início de um `atomo`); logo, o próximo `{` abre o corpo.

> **Observações sobre a sintaxe do `while` (v2):**
>
> - Um `while_cmd` é um comando e **não leva `;`** depois (igual a
>   `func_decl`). Após o `}` que fecha o corpo, o próximo comando ou a expressão
>   final do bloco começa diretamente, sem ponto-e-vírgula separador.
> - Todo bloco `{ ... }` (programa, corpo de `def`/`fn`, ramos de `if`) exige
>   uma expressão final. O corpo do `while` (`bloco_cmd`) é a exceção: é
>   composto apenas de comandos, sem expressão final.
> - Um `while` dentro do corpo de outro `while` também não leva `;`.

Sobre registros, acesso e atribuição a campo (v3):

- Um `registro` é uma **expressão** (um `atomo`): `{ f1: e1, ..., fn: en }`
  tem $n \geq 0$ campos, separados por vírgula (sem vírgula final). Os nomes
  dos campos de um mesmo literal devem ser **distintos**; repetir um nome é um
  **erro de sintaxe**. `{}` é o registro vazio.
- **Bloco ou registro?** Um `{` em posição de `atomo` abre um `bloco` ou um
  `registro`. A decisão usa dois tokens de lookahead: é `registro` se o `{` for
  seguido de `}` ou de `NOME :` (`COLON`); caso contrário, é `bloco`. Não há
  ambiguidade: todo `bloco` precisa de uma expressão final, então `{ }` nunca é
  um `bloco` válido; e um `bloco` não pode começar com `NOME :`, pois `:` não
  inicia nem continua uma expressão (`NOME :=` é `ASSIGN`, outro token).
- Nas posições em que a gramática exige um `bloco` ou `bloco_cmd` (ramos de
  `if`, corpo de `def` e de `fn`, corpo de `while`), o `{` **sempre** abre um
  bloco, nunca um registro. Para produzir um registro nessas posições, ele deve
  ser a expressão final do bloco: `fn(a) { { x: a } }`.
- Um `sufixo` é uma chamada `( args )` ou um acesso a campo `. NOME`, e os
  sufixos associam à esquerda e se combinam livremente: `f(1).g(2).h`,
  `a.b.c`, `o.m()`. Têm a maior precedência da linguagem (mais que o sinal
  unário): `-r.x` é `-(r.x)`.
- Os nomes de campo pertencem à categoria `NOME` e, portanto, **não podem ser
  palavras reservadas**. Eles não são variáveis: vivem num espaço de nomes
  próprio (veja §3.4).
- O alvo de uma atribuição pode ser uma variável (`NOME := exp`, como na v1) ou
  um `acesso` (`e . NOME := exp`), isto é, uma expressão pós-fixa cuja última
  operação é um acesso a campo. Atribuir a outras expressões (`f() := 1`,
  `(a + b) := 1`) é erro de sintaxe. Como um `acesso` pode ter tamanho
  arbitrário, o parser não consegue decidir entre `atribuicao` e `exp ;` por
  lookahead fixo. Uma implementação típica lê uma `exp` e, se o próximo token for
  `:=`, verifica se a expressão lida é uma variável ou um acesso a campo; se for,
  é uma atribuição, e se não for, é erro de sintaxe.
- `atribuicao`, como `var_decl` e `exp`, termina em `;`.

## 3. Semântica Operacional (*Big-Step*)

### 3.1 Domínios Semânticos

| Domínio | Notação | Descrição |
|---|---|---|
| Reais | $ℝ$ | Os números reais. |
| Locais / Endereços | $\mathrm{Loc}$ | Conjunto infinito e enumerável de endereços de memória. |
| Campos | $\mathrm{Fld}$ | Nomes de campos de registros (v3). Não são variáveis: $\mathrm{Fld}$ não interage com $\mathrm{Env}$. |
| Referências | $\mathrm{Ref} = \{ \mathsf{ref}(\ell) \mid \ell \in \mathrm{Loc} \}$ | Referência a um registro na memória (v3). É assim que um registro é visto como valor. |
| *Closures* | $\mathrm{Clo} = \mathrm{Var}^* \times \mathrm{Bloco} \times \mathrm{Env}$ | Tripla: (parâmetros, bloco do corpo, ambiente de criação). |
| Valores | $\mathrm{Val} = ℝ \cup \mathrm{Clo} \cup \mathrm{Ref} \cup \{ \mathbf{erro} \}$ | Valores denotáveis na avaliação. (v3: acrescenta $\mathrm{Ref}$.) |
| Registros (objetos) | $\mathrm{Obj} = \mathrm{Fld} \rightharpoonup \mathrm{Val}$ | Mapeamento parcial, de domínio finito, de nomes de campos para valores (v3). |
| Ambientes | $\mathrm{Env} = \mathrm{Var} \rightharpoonup \mathrm{Loc}$ | Mapeamento de nomes de variáveis para endereços de memória. |
| Memória (*Store*) | $\mathrm{Store} = \mathrm{Loc} \rightharpoonup (\mathrm{Val} \cup \mathrm{Obj})$ | Mapeamento parcial de endereços de memória para valores ou, na v3, para registros. |

Na v3, um endereço da memória guarda uma de duas coisas: um **valor** (os
endereços de variáveis, parâmetros e funções nomeadas, alocados como na v1/v2)
ou um **registro** (os endereços alocados pela regra (Reg), que são os únicos
que aparecem dentro de uma $\mathsf{ref}(\ell)$). Duas invariantes valem sempre:

- todo endereço na imagem de um ambiente $\rho$ guarda um valor em $\mathrm{Val}$;
- uma expressão nunca avalia para um elemento de $\mathrm{Obj}$: avalia para uma
  referência $\mathsf{ref}(\ell)$, e o registro em si só existe na memória.

É essa indireção (a variável guarda uma referência, que aponta para o registro)
que dá **identidade** aos registros.


### 3.2 Framework semântico

A semântica opera sob um modelo de memória de dois níveis ($\rho, \sigma$):

1. **Avaliação de Comandos:** $\langle c, \rho, \sigma \rangle \Downarrow \langle \rho_1, \sigma_1 \rangle$  
   (Um comando $c$ executado no ambiente $\rho$ e memória $\sigma$ produz um novo ambiente $\rho_1$ e uma nova memória $\sigma_1$)

2. **Avaliação de Expressões e Blocos:** $\langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle$  
   (Uma expressão ou bloco $e$ avaliado no ambiente $\rho$ e memória $\sigma$ produz um valor $v \in \mathrm{Val}$ e atualiza a memória para $\sigma_1$)

3. **Execução do Corpo de um Laço** (v2): $\langle b, \rho, \sigma \rangle \Downarrow_s \sigma_1$  
   (Uma sequência de comandos $b$, o corpo de um `while`, executada no ambiente $\rho$ e memória $\sigma$ produz uma nova memória $\sigma_1$. O ambiente final é descartado: o escopo do corpo termina junto com ele, mas a memória persiste)

A v3 não acrescenta relações. Registros alteram apenas a **memória**: as regras
da v3 nunca modificam o ambiente $\rho$ (um campo não é uma variável).


### 3.3 Regras de Avaliação de Comandos (*Statements*)

#### Declaração de Variável (`var`)
Avalia a expressão inicializadora, aloca um novo endereço livre $\ell$ na memória e estende o ambiente local com o vínculo $x \mapsto \ell$:

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle \qquad \ell \notin \mathrm{dom}(\sigma_1)
}{
  \langle \mathtt{var}\ x\\, \mathtt{:=} e; \, \rho, \sigma \rangle \Downarrow \langle \rho[x \mapsto \ell],\\, \sigma_1[\ell \mapsto v] \rangle
} \quad \text{(VarDecl)}
$$

#### Atribuição Mutável (`:=`)

Busca o endereço $\ell = \rho(x)$ já existente e substitui o valor contido nesse endereço na memória. O ambiente $\rho$ permanece inalterado:

$$
\frac{
  \rho(x) = \ell \qquad \langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle
}{
  \langle x\\, \mathtt{:=} e; \, \rho, \sigma \rangle \Downarrow \langle \rho,\\, \sigma_1[\ell \mapsto v] \rangle
} \quad \text{(Assign)}
$$

$$
\frac{
  x \notin \mathrm{dom}(\rho)
}{
  \langle x\\, \mathtt{:=} e; \, \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(AssignNaoDeclarada)}
$$

#### Atribuição a Campo (`e.f :=`) — v3

Avalia primeiro a expressão $e_o$ do lado esquerdo, que deve produzir uma
referência $\mathsf{ref}(\ell)$ a um registro, e depois a expressão $e$ do lado
direito. Em seguida, atualiza (ou **cria**, se ainda não existir) o campo $f$ do
registro guardado em $\ell$. O ambiente $\rho$ permanece inalterado:

$$
\frac{
  \begin{matrix}
  \langle e_o, \rho, \sigma \rangle \Downarrow \langle \mathsf{ref}(\ell),\\, \sigma_1 \rangle \qquad
  \langle e, \rho, \sigma_1 \rangle \Downarrow \langle v,\\, \sigma_2 \rangle \qquad
  \sigma_2(\ell) = o
  \end{matrix}
}{
  \langle e_o.f\\, \mathtt{:=} e; \, \rho, \sigma \rangle \Downarrow \langle \rho,\\, \sigma_2[\ell \mapsto o[f \mapsto v]] \rangle
} \quad \text{(AssignCampo)}
$$

$$
\frac{
  \langle e_o, \rho, \sigma \rangle \Downarrow \langle v_o,\\, \sigma_1 \rangle \qquad v_o \notin \mathrm{Ref}
}{
  \langle e_o.f\\, \mathtt{:=} e; \, \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(AssignCampoNaoRegistro)}
$$

Observações:

- **Ordem de avaliação.** $e_o$ é avaliada antes de $e$. Se $e_o$ não for uma
  referência, ocorre erro **sem** avaliar $e$.
- **Releitura do registro.** O registro é lido de $\sigma_2$, e não de
  $\sigma_1$, porque a avaliação de $e$ pode ter alterado o próprio registro
  (por exemplo, por meio de uma chamada de função). A atribuição preserva essas
  alterações nos demais campos.
- **Criação de campos.** Diferentemente de (Assign), em que o nome precisa já
  estar declarado, atribuir a um campo inexistente **não é erro**: o campo
  passa a existir. É isso que permite `var este := {}; este.n := 0;`.
  Campos não são declarados.
- **Efeito.** Apenas $\sigma$ muda, e todas as referências ao mesmo registro
  passam a enxergar o novo valor do campo (aliasing).

#### Declaração de Função Nomeada (`def`)

Aloca um endereço de memória $\ell_f$ para armazenar a closure da função. A
closure captura o ambiente $\rho_1$ que inclui a própria função $f$,
viabilizando **recursão nativa**:

$$
\frac{
  \ell_f \notin \mathrm{dom}(\sigma) \qquad \rho_1 = \rho[f \mapsto \ell_f] \qquad v_f = \mathsf{clo}((p_1, \ldots, p_n),\\, e_{\text{corpo}},\\, \rho_1)
}{
  \langle \mathtt{def}\ f(p_1, \ldots, p_n)\ e_{\text{corpo}}, \rho, \sigma \rangle \Downarrow \langle \rho_1,\\, \sigma[\ell_f \mapsto v_f] \rangle
} \quad \text{(FunDecl)}
$$

#### Expressão como Comando (`exp ;`)

Avalia a expressão por seus efeitos colaterais na memória e descarta o valor
resultante $v$:

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle \qquad v \neq \mathbf{erro}
}{
  \langle e;, \rho, \sigma \rangle \Downarrow \langle \rho, \sigma_1 \rangle
} \quad \text{(ExprStmt)}
$$

#### Laço (`while`) — v2

O corpo de um laço é uma sequência de comandos executada em ordem, alterando a
memória $\sigma_0 \to \sigma_1 \to \dots \to \sigma_n$. Diferentemente de um
bloco, **não há expressão final**, e o ambiente final $\rho_n$ é **descartado**:
o escopo do corpo termina com a execução do corpo, mas a memória persiste. (Para
$n = 0$, tem-se $\sigma_n = \sigma_0$: o corpo vazio não altera a memória.)

$$
\frac{
  \langle c_1, \rho, \sigma_0 \rangle \Downarrow \langle \rho_1, \sigma_1 \rangle \quad \dots \quad \langle c_n, \rho_{n-1}, \sigma_{n-1} \rangle \Downarrow \langle \rho_n, \sigma_n \rangle
}{
  \langle \{ c_1 \dots c_n \}, \rho, \sigma_0 \rangle \Downarrow_s \sigma_n
} \quad \text{(BlocoCmd)}
$$

A condição é numérica, como em `if`: o valor $0$ é falso, e qualquer outro
número é verdadeiro. Se a condição é falsa, o laço termina sem executar o
corpo. O ambiente de um comando `while` **não muda**:

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle 0, \sigma_1 \rangle
}{
  \langle \mathtt{while}\ e\ b, \rho, \sigma \rangle \Downarrow \langle \rho, \sigma_1 \rangle
} \quad \text{(WhileFalso)}
$$

Se a condição é verdadeira, o corpo é executado e **o laço é repetido** a partir
da memória resultante:

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

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle v_c, \sigma_1 \rangle \qquad v_c \in \mathrm{Ref}
}{
  \langle \mathtt{while}\ e\ b, \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(WhileCondRegistro) — v3}
$$

Observações:

- **Recursão.** A última premissa de (WhileVerd) contém o próprio `while`: é
  essa recursão que faz o laço repetir. Em uma implementação, ela corresponde a
  uma iteração.
- **Ambiente.** Cada iteração executa o corpo a partir do mesmo $\rho$. Logo, um
  `var` declarado no corpo não é visível depois do laço, e cada iteração aloca
  um novo endereço para ele (closures criadas em iterações distintas não
  compartilham essa variável).
- **Memória.** É a memória, passada de premissa em premissa
  ($\sigma \to \sigma_1 \to \sigma_2 \to \sigma_3$), que carrega o "progresso"
  do laço: a condição só muda de valor porque o corpo (ou a própria condição)
  altera a memória.
- **Não terminação.** Se a condição for sempre verdadeira (por exemplo,
  `while 1 { }`), (WhileVerd) é reaplicada indefinidamente e **não existe
  derivação**: a semântica passa a ser **parcial**. O determinismo se mantém: em
  cada ponto, no máximo uma regra se aplica, conforme o valor da condição.
- **Erros.** Valem a convenção da §3.5 e as regras (WhileCondFuncao) e, na v3,
  (WhileCondRegistro), análogas a (IfCondFuncao) e (IfCondRegistro).

Exemplo:

```text
var i := 0;
var soma := 0;
while i < 5 {
    soma := soma + i;
    i := i + 1;
}
soma                     // 10
```


### 3.4 Regras de Avaliação de Expressões e Blocos

#### Blocos e Retorno Implícito (`Block`)

Executa sequencialmente uma cadeia de comandos alterando a memória $\sigma_0
\to \sigma_1 \dots \to \sigma_n$ em um subescopo local. O resultado do bloco é
o valor da expressão final $e_{\text{final}}$:

$$
\frac{
  \begin{matrix}
  \langle c_1, \rho, \sigma_0 \rangle \Downarrow \langle \rho_1, \sigma_1 \rangle \quad \dots \quad \langle c_n, \rho_{n-1}, \sigma_{n-1} \rangle \Downarrow \langle \rho_n, \sigma_n \rangle \qquad
  \langle e_{\text{final}}, \rho_n, \sigma_n \rangle \Downarrow \langle v, \sigma_{n+1} \rangle
  \end{matrix}
}{
  \langle \{ c_1 \dots c_n\ e_{\text{final}} \}, \rho, \sigma_0 \rangle \Downarrow \langle v, \sigma_{n+1} \rangle
} \quad \text{(Block)}
$$


#### Números e Variáveis

$$
\frac{
}{
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
\frac{
}{
  \langle \mathtt{fn}\ (p_1, \ldots, p_n)\ e_{\text{bloco}},\\, \rho, \sigma \rangle \Downarrow \langle \mathsf{clo}((p_1, \ldots, p_n),\\, e_{\text{bloco}},\\, \rho),\\, \sigma \rangle
} \quad \text{(Lam)}
$$

#### Aplicação de Função (`Call`)
Avalia a função e os argumentos, aloca endereços de memória distintos $\ell_1, \ldots, \ell_n$ para cada parâmetro formal no ambiente da closure ($\rho_0$) e avalia o corpo:

$$
\frac{
  \begin{matrix}
  \langle e_f, \rho, \sigma_0 \rangle \Downarrow \langle \mathsf{clo}((p_1, \ldots, p_n), e_{\text{corpo}}, \rho_0),\\, \sigma_1 \rangle \\
  \langle a_1, \rho, \sigma_1 \rangle \Downarrow \langle v_1, \sigma_2 \rangle \quad \dots \quad \langle a_n, \rho, \sigma_n \rangle \Downarrow \langle v_n, \sigma_{n+1} \rangle \\
  \ell_1, \ldots, \ell_n \notin \mathrm{dom}(\sigma_{n+1}) \quad \text{distintos} \\
  \rho_1 = \rho_0[p_1 \mapsto \ell_1, \dots, p_n \mapsto \ell_n] \qquad \sigma_1 = \sigma_{n+1}[\ell_1 \mapsto v_1, \dots, \ell_n \mapsto v_n] \\
  \langle e_{\text{corpo}}, \rho_1, \sigma_1 \rangle \Downarrow \langle v, \sigma_2 \rangle
  \end{matrix}
}{
  \langle e_f(a_1, \ldots, a_n), \rho, \sigma_0 \rangle \Downarrow \langle v, \sigma_2 \rangle
} \quad \text{(App)}
$$

#### Erros na Aplicação

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

$$
\frac{
  \langle c, \rho, \sigma_0 \rangle \Downarrow \langle v_c, \sigma_1 \rangle \qquad v_c \in \mathrm{Ref}
}{
  \langle \mathtt{if}\ c\ b_{\text{then}}\ \mathtt{else}\ b_{\text{else}}, \rho, \sigma_0 \rangle \Downarrow \mathbf{erro}
} \quad \text{(IfCondRegistro) — v3}
$$

#### Operadores Binários (*Lifted*)

$$
\frac{
  \langle e_1, \rho, \sigma_0 \rangle \Downarrow \langle v_1, \sigma_1 \rangle \qquad
  \langle e_2, \rho, \sigma_1 \rangle \Downarrow \langle v_2, \sigma_2 \rangle
}{
  \langle e_1 \text{ op } e_2, \rho, \sigma_0 \rangle \Downarrow \langle f_{\mathrm{op}}^{\uparrow}(v_1, v_2), \sigma_2 \rangle
} \quad \text{(OpBinario)}
$$

Nota (v3): a função $f_{\mathrm{op}}^{\uparrow}$ é a versão *lifted* da operação
$f_{\mathrm{op}}$ sobre os reais: $f_{\mathrm{op}}^{\uparrow}(v_1, v_2) =
f_{\mathrm{op}}(v_1, v_2)$ se $v_1, v_2 \in ℝ$, e $\mathbf{erro}$ caso
contrário. Em particular, aplicar um operador (inclusive `==`) a um registro, ou
seja, a uma $\mathsf{ref}(\ell)$, é erro: `==` compara números, e não a
identidade de registros.

#### Registros e Acesso a Campo — v3

**Criação de registro.** Os campos são avaliados da esquerda para a direita, e
um novo endereço $\ell$, livre, passa a guardar o registro construído. O valor
da expressão é a referência $\mathsf{ref}(\ell)$ (para $n = 0$, o registro vazio
$\{\}$):

$$
\frac{
  \begin{matrix}
  \langle e_1, \rho, \sigma_0 \rangle \Downarrow \langle v_1, \sigma_1 \rangle \quad \dots \quad \langle e_n, \rho, \sigma_{n-1} \rangle \Downarrow \langle v_n, \sigma_n \rangle \\
  \ell \notin \mathrm{dom}(\sigma_n) \qquad o = \{ f_1 \mapsto v_1, \ldots, f_n \mapsto v_n \}
  \end{matrix}
}{
  \langle \{ f_1 : e_1, \ldots, f_n : e_n \}, \rho, \sigma_0 \rangle \Downarrow \langle \mathsf{ref}(\ell),\\, \sigma_n[\ell \mapsto o] \rangle
} \quad \text{(Reg)}
$$

**Acesso a campo.** Avalia $e$, que deve produzir uma referência a um registro, e
devolve o valor do campo $f$:

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle \mathsf{ref}(\ell),\\, \sigma_1 \rangle \qquad \sigma_1(\ell) = o \qquad f \in \mathrm{dom}(o)
}{
  \langle e.f, \rho, \sigma \rangle \Downarrow \langle o(f),\\, \sigma_1 \rangle
} \quad \text{(Campo)}
$$

**Erros.**

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle \qquad v \notin \mathrm{Ref}
}{
  \langle e.f, \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(CampoNaoRegistro)}
$$

$$
\frac{
  \langle e, \rho, \sigma \rangle \Downarrow \langle \mathsf{ref}(\ell),\\, \sigma_1 \rangle \qquad \sigma_1(\ell) = o \qquad f \notin \mathrm{dom}(o)
}{
  \langle e.f, \rho, \sigma \rangle \Downarrow \mathbf{erro}
} \quad \text{(CampoInexistente)}
$$

Observações:

- **Identidade e aliasing.** (Reg) é a única regra que aloca registros; o valor
  de um registro é uma referência. Logo, `var b := a;` copia a referência, e `a`
  e `b` passam a denotar o **mesmo** registro: uma atribuição a campo feita
  por meio de `b` é vista por meio de `a`. O mesmo vale para a passagem de
  argumentos em (App): o parâmetro recebe uma cópia da referência, e não do
  registro.
- **Campos não são variáveis.** Os nomes de campo $f$ não são buscados em
  $\rho$: `{ x: x }` é um registro cujo campo `x` recebe o valor da variável
  `x`. Por isso, também não há regra de "campo não ligado" análoga a
  (VarNaoLigada): ler um campo ausente é o erro (CampoInexistente), e atribuir a
  um campo ausente é a criação de um campo (§3.3).
- **Ambiente.** Nenhuma das regras acima altera $\rho$. Só $\sigma$ muda ((Reg)
  aloca; (AssignCampo) atualiza).
- **Métodos.** Não existe regra para "invocar um método". Em `c.inc()`, a função
  é a expressão `c.inc`, avaliada por (Campo) para uma closure, e (App) a aplica
  como qualquer outra. A closure carrega o seu próprio ambiente de criação
  $\rho_0$; nenhum "receptor" é passado. Se um método precisa do objeto, ele o
  alcança por uma variável capturada nesse ambiente (por convenção, `este`).
- **Erros.** Valem a convenção da §3.5 e as regras (CampoNaoRegistro),
  (CampoInexistente), (AssignCampoNaoRegistro), (IfCondRegistro) e
  (WhileCondRegistro). Chamar um registro como função cai em (AppNaoFuncao), já
  que $\mathrm{Ref} \cap \mathrm{Clo} = \emptyset$.
- **Fora do escopo da v3.** Não há remoção de campos, teste de existência de
  campo, enumeração de campos nem comparação de identidade entre registros.

Exemplos:

```text
var p := { x: 1, y: 2 };
var q := p;              // q e p referenciam o MESMO registro
q.x := 10;
p.x + p.y                // 12
```

```text
def Contador() {
    var este := {};
    este.n := 0;
    este.inc := fn() { este.n := este.n + 1; este.n };
    este.get := fn() { este.n };
    este
}
var c1 := Contador();
var c2 := Contador();
c1.inc();
c1.inc();
c2.inc();
c1.get() + 1000 * c2.get()       // 1002
```

No segundo exemplo, cada chamada a `Contador()` executa (Reg) uma vez (para
`{}`), alocando um registro novo, e (VarDecl) uma vez para `este`. As closures
`inc` e `get` de `c1` capturam o `este` de `c1`; as de `c2`, o de `c2`. A
mutação de `este.n` por (AssignCampo) altera o registro compartilhado por
`este`, por `c1` e pelas closures: é isso que faz `c1.get()` enxergar o que
`c1.inc()` fez.


### 3.5 Convenção Monádica de Propagação de Erros

> Se qualquer premissa da forma $\langle e, \rho, \sigma \rangle \Downarrow \mathbf{erro}$, $\langle c, \rho, \sigma \rangle \Downarrow \mathbf{erro}$ ou (v2) $\langle b, \rho, \sigma \rangle \Downarrow_s \mathbf{erro}$ produzir $\mathbf{erro}$, a avaliação da regra é interrompida imediatamente e a conclusão de toda a derivação é $\mathbf{erro}$.

A v3 não introduz novas relações, então a convenção acima vale sem alteração
para as regras de registros: por exemplo, se a avaliação de $e_i$ em (Reg) ou de
$e$ em (AssignCampo) produzir $\mathbf{erro}$, o resultado de toda a derivação é
$\mathbf{erro}$.
