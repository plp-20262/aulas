# Especificação de `algora` (v2)

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

A v2 apenas acrescenta: nenhuma regra da v1 muda (a convenção de erros da §3.5
só passa a cobrir também a nova relação $\Downarrow_s$). Nas seções abaixo,
`← NOVO` marca o que é novo em relação a Aljabr, e `← NOVO (v2)` marca o que
foi introduzido na v2. Como consequência da v2, `while` passa a ser palavra
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
> como `**` vem antes de `*` e `==` vem antes de `=`. Identificadores da
> categoria `NOME` aceitam letras maiúsculas e minúsculas.


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
unario      ::= [ + | - ] chamada
chamada     ::= atomo { LPAREN [ args ] RPAREN }
atomo       ::= INTEIRO | NOME | LPAREN exp RPAREN | bloco

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

## 3. Semântica Operacional (*Big-Step*)

### 3.1 Domínios Semânticos

| Domínio | Notação | Descrição |
|---|---|---|
| Reais | $ℝ$ | Os números reais. |
| Locais / Endereços | $\mathrm{Loc}$ | Conjunto infinito e enumerável de endereços de memória. |
| *Closures* | $\mathrm{Clo} = \mathrm{Var}^* \times \mathrm{Bloco} \times \mathrm{Env}$ | Tripla: (parâmetros, bloco do corpo, ambiente de criação). |
| Valores | $\mathrm{Val} = ℝ \cup \mathrm{Clo} \cup \{ \mathbf{erro} \}$ | Valores denotáveis na avaliação. |
| Ambientes | $\mathrm{Env} = \mathrm{Var} \rightharpoonup \mathrm{Loc}$ | Mapeamento de nomes de variáveis para endereços de memória. |
| Memória (*Store*) | $\mathrm{Store} = \mathrm{Loc} \rightharpoonup \mathrm{Val}$ | Mapeamento parcial de endereços de memória para valores. |


### 3.2 Framework semântico

A semântica opera sob um modelo de memória de dois níveis ($\rho, \sigma$):

1. **Avaliação de Comandos:** $\langle c, \rho, \sigma \rangle \Downarrow \langle \rho_1, \sigma_1 \rangle$  
   (Um comando $c$ executado no ambiente $\rho$ e memória $\sigma$ produz um novo ambiente $\rho_1$ e uma nova memória $\sigma_1$)

2. **Avaliação de Expressões e Blocos:** $\langle e, \rho, \sigma \rangle \Downarrow \langle v, \sigma_1 \rangle$  
   (Uma expressão ou bloco $e$ avaliado no ambiente $\rho$ e memória $\sigma$ produz um valor $v \in \mathrm{Val}$ e atualiza a memória para $\sigma_1$)

3. **Execução do Corpo de um Laço** (v2): $\langle b, \rho, \sigma \rangle \Downarrow_s \sigma_1$  
   (Uma sequência de comandos $b$, o corpo de um `while`, executada no ambiente $\rho$ e memória $\sigma$ produz uma nova memória $\sigma_1$. O ambiente final é descartado: o escopo do corpo termina junto com ele, mas a memória persiste)


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
- **Erros.** Valem a convenção da §3.5 e a regra (WhileCondFuncao), análoga a
  (IfCondFuncao).

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

#### Operadores Binários (*Lifted*)

$$
\frac{
  \langle e_1, \rho, \sigma_0 \rangle \Downarrow \langle v_1, \sigma_1 \rangle \qquad
  \langle e_2, \rho, \sigma_1 \rangle \Downarrow \langle v_2, \sigma_2 \rangle
}{
  \langle e_1 \text{ op } e_2, \rho, \sigma_0 \rangle \Downarrow \langle f_{\mathrm{op}}^{\uparrow}(v_1, v_2), \sigma_2 \rangle
} \quad \text{(OpBinario)}
$$


### 3.5 Convenção Monádica de Propagação de Erros

> Se qualquer premissa da forma $\langle e, \rho, \sigma \rangle \Downarrow \mathbf{erro}$, $\langle c, \rho, \sigma \rangle \Downarrow \mathbf{erro}$ ou (v2) $\langle b, \rho, \sigma \rangle \Downarrow_s \mathbf{erro}$ produzir $\mathbf{erro}$, a avaliação da regra é interrompida imediatamente e a conclusão de toda a derivação é $\mathbf{erro}$.

