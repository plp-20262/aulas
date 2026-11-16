# Aula 16 (fecho) — 11/nov — Unidade 6: o comando `while`

> **Posição no plano de aulas.** Aula 16, Unidade 6 (controle de fluxo). A
> Aula 16 foi dada em 11/nov apenas em parte. Este roteiro é o **fecho** da
> aula, aplicado em 16/nov, antes de iniciar a Aula 17 (Unidade 7, tipos
> algébricos).
>
> **Já coberto em 11/nov** (conforme relato): atribuição e sequenciamento;
> linguagens orientadas a expressão × orientadas a comando; tabela de síntese
> corrente atualizada. **Pendente:** o comando `while` e sua especificação
> formal. `if` e blocos já existem em Algora. A implementação de Algora v2 (com
> `while`) já está pronta.
>
> Tema: com estado e mutação, passa a fazer sentido **avaliar a mesma
> expressão várias vezes**. Daí a motivação para controle de fluxo e, em
> particular, para laços imperativos.
>
> Duração prevista: ≈ 15 min. Os resultados dos exemplos vêm das regras, não
> de execução.

| # | Bloco                                      | Min |
|---|--------------------------------------------|-----|
| 1 | Gancho: por que agora faz sentido repetir  | 3   |
| 2 | Sintaxe do `while`                         | 2   |
| 3 | Semântica: as regras                       | 6   |
| 4 | Um exemplo e sua tabela de rastreamento    | 3   |
| 5 | Fecho e ponte para a Aula 17               | 1   |


## 1. Gancho

Lembre do que concluímos na Aula 14 (§8): em `aljabr`, um laço como

```text
enquanto (i < 10) corpo
```

não faz sentido, porque `i < 10` **sempre** vale o mesmo. Ou o corpo nunca
executa, ou executa para sempre. Repetição só existia como recursão.

Agora temos store. Avaliar `i < 10` duas vezes pode dar resultados
diferentes, porque o corpo pode ter alterado `i` entre as avaliações. Reavaliar
uma expressão deixou de ser desperdício: **é o que faz o programa progredir**.

> Pergunta à turma: o que precisa acontecer, entre uma avaliação e a
> seguinte da condição, para que o laço termine?
> (Resposta: o corpo precisa modificar o store.)


## 2. Sintaxe

Um novo comando. Como `def`, `while` **não produz valor**: é um comando, não
uma expressão.

```text
comando    ::= func_decl
             | var_decl ;
             | atribuicao ;
             | while_cmd                      ← NOVO (sem ";")
             | exp ;

while_cmd  ::= while exp bloco_cmd            ← NOVO
bloco_cmd  ::= LBRACE { comando } RBRACE      ← NOVO
```

- `while` é a sexta palavra reservada (`var`, `def`, `fn`, `if`, `else`, `while`).
- O corpo é uma sequência de **comandos**, sem expressão final.
- A condição é numérica, como no `if`: `0` é falso; qualquer outro número,
  verdadeiro. Uma closure na condição é `erro`.
- Sintaxe abstrata: `While(cond, corpo)`.

> Nota: o parser continua LL(1). O token `WHILE` decide a alternativa em
> `comando`, e em `while i < 3 {` a condição já terminou quando o `{` aparece.


## 3. Semântica

A relação de comandos continua sendo
$\langle c,\rho,\sigma\rangle \rightarrow \langle\rho',\sigma'\rangle$.

**Corpo do laço.** Uma sequência de comandos executa em ordem. O ambiente final
é **descartado**: o escopo do corpo morre, mas o store persiste.

$$
\frac{
  \langle c_1,\rho,\sigma_0\rangle \rightarrow \langle\rho_1,\sigma_1\rangle \quad\cdots\quad
  \langle c_n,\rho_{n-1},\sigma_{n-1}\rangle \rightarrow \langle\rho_n,\sigma_n\rangle
}{
  \langle \{c_1 \dots c_n\},\rho,\sigma_0\rangle \Downarrow_{s} \sigma_n
} \quad \text{(BlocoCmd)}
$$

**Condição falsa:** o laço termina. O store é o que a condição deixou, e o
ambiente não muda.

$$
\frac{
  \langle c,\rho,\sigma\rangle \Downarrow \langle 0,\sigma_1\rangle
}{
  \langle \mathtt{while}\ c\ b,\rho,\sigma\rangle \rightarrow \langle\rho,\sigma_1\rangle
} \quad \text{(WhileFalso)}
$$

**Condição verdadeira:** executa o corpo e **repete o laço** com o store
atualizado.

$$
\frac{
  \langle c,\rho,\sigma\rangle \Downarrow \langle n,\sigma_1\rangle \ (n\in ℝ,\ n\neq 0) \qquad
  \langle b,\rho,\sigma_1\rangle \Downarrow_{s} \sigma_2 \qquad
  \langle \mathtt{while}\ c\ b,\rho,\sigma_2\rangle \rightarrow \langle\rho,\sigma_3\rangle
}{
  \langle \mathtt{while}\ c\ b,\rho,\sigma\rangle \rightarrow \langle\rho,\sigma_3\rangle
} \quad \text{(WhileVerd)}
$$

**Condição que é função:**

$$
\frac{
  \langle c,\rho,\sigma\rangle \Downarrow \langle v_c,\sigma_1\rangle \qquad v_c\in\mathrm{Clo}
}{
  \langle \mathtt{while}\ c\ b,\rho,\sigma\rangle \rightarrow \mathbf{erro}
} \quad \text{(WhileCondFuncao)}
$$

Se a condição ou algum comando do corpo produz `erro`, vale a convenção de
propagação de `erro` de Algora.

### Pontos para comentar

1. **A 3ª premissa de (WhileVerd) contém o próprio `while`.** A regra é
   recursiva, e é essa recursão que faz o laço repetir. Compare com `(App)`: lá
   a recursão estava em chamar o corpo de uma função; aqui, em chamar o próprio
   comando.
2. **O store viaja de premissa em premissa:** $\sigma \to \sigma_1 \to \sigma_2
   \to \sigma_3$. É ele que carrega o "progresso" do laço.
3. **A semântica agora é parcial.** Em `while 1 { }` não existe derivação
   alguma: a regra `(WhileVerd)` se reaplica para sempre. É a primeira vez no
   curso que a não-terminação aparece explicitamente nas regras. O
   determinismo continua valendo; a totalidade, não.
4. **O ambiente não muda:** um `var` dentro do corpo não é visível depois do
   laço.

### Regra → implementação

| Regra                           | Na implementação                                                         |
|---------------------------------|--------------------------------------------------------------------------|
| (WhileVerd) + (WhileFalso)      | um laço Python: avalia a condição; se `0`, para; senão, executa o corpo  |
| (BlocoCmd), ambiente descartado | o corpo executa sobre uma cópia do ambiente; o store é compartilhado     |
| (WhileCondFuncao)               | closure na condição devolve `Erro`                                       |

> A recursão das regras vira iteração no interpretador: laços longos não
> estouram a pilha de Python.

*(Se sobrar tempo: `while c b` equivale a uma função recursiva auxiliar, mas
sem o custo de pilha. É o mesmo raciocínio de açúcar sintático da Aula 15,
§5.6.)*


## 4. Exemplo

```text
var i := 0;
var soma := 0;
while i < 5 {
    soma := soma + i;
    i := i + 1;
}
soma                     // 10
```

Tabela de rastreamento (como nas aulas de RPN):

| iteração | `i` antes | `i < 5` | `soma` depois |
|----------|-----------|---------|---------------|
| 1        | 0         | 1       | 0             |
| 2        | 1         | 1       | 1             |
| 3        | 2         | 1       | 3             |
| 4        | 3         | 1       | 6             |
| 5        | 4         | 1       | 10            |
| fim      | 5         | 0       | 10            |

Cada linha é uma aplicação de `(WhileVerd)`; a última é `(WhileFalso)`.


## 5. Fecho e ponte para a Aula 17

- Estado e mutação tornaram natural **repetir** a avaliação de uma expressão.
  `while` é a forma mais direta disso.
- Em Algora temos um comando de repetição, mas os dados ainda são apenas
  **números** (e funções). A Aula 17 (Unidade 7, tipos algébricos) começa
  exatamente desse limite: problemas reais exigem estruturas compostas
  (soma e produto).


## Tarefa e exercícios

**Tarefa prevista no plano de aulas (fora de aula):** estender o interpretador
com as construções de controle. Em Algora, `if` e blocos já existem; resta o
`while`, a partir das regras desta aula.

**Exercícios opcionais:**

1. Derive, com as regras, a execução de
   `var i := 0; while i < 2 { i := i + 1; } i`.
2. Na Aula 14 (§8.2) perguntamos que sentido teria um `enquanto` em `aljabr`.
   Com as regras de hoje, o que mudou? Explique em termos do store.
