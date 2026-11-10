# Aula 15 — 08/Nov — Conclusão Unidade 4 (5/4)

> Tema da aula: `aljabr` v3 (recursão e condicional) e fechamento da
> Unidade 4: por que `aljabr` é uma linguagem **funcional pura**.
>
> - início da tabela de síntese de paradigmas
> - ponte para a Unidade 5 (estado e mutação)


### 5.6 Comentário: `letrec` e o `def` de Python

O nosso `letrec` lembra bastante o `def` de Python, principalmente por um motivo: porque uma
função definida com ambas pode invocar a si própria.

```python
def fat(n):
    return 1 if n == 0 else n * fat(n - 1)
```

```text
letrec fat = fn (n) => if n == 0 then 1 else n * fat(n - 1) in
fat(5)
```

O importante é que são parecidos, mas **não exatamente iguais**, nem na sintaxe nem na semântica:

| Aspecto                 | `def` (Python)                                              | `letrec` (`aljabr`)                                              |
|-------------------------|-------------------------------------------------------------|------------------------------------------------------------------|
| Categoria               | _comando_ (não produz valor)                                | _expressão_ (produz o valor de `e₂`)                             |
| Escopo do nome          | todo o bloco envolvente (módulo ou função)                  | só o corpo `e₂` e a própria função                               |
| Como a recursão ocorre  | o nome é procurado no escopo envolvente **na hora da chamada** | o closure captura um ambiente que **já contém** o próprio closure (a equação de `(LetRec)`) |
| Ligação do nome         | é uma atribuição: pode ser refeita depois                   | imutável                                                         |
| Recursão mútua          | sim, naturalmente                                           | não: uma função por vez                                          |

> **Pergunta:** o que devolve `g(3)` no programa Python abaixo?
>
> ```python
> def f(n):
>     return 1 if n == 0 else n * f(n - 1)
>
> g = f
>
> def f(n):
>     return 0
>
> print(g(3))
> ```
> <details>
> <summary>Clique pra ver a resposta</summary>
>
> <br>Resposta: `0`, e não `6`. O corpo de `g` (a função original) procura `f` no
> momento da chamada e encontra a **nova** definição. Em `aljabr`, isso não
> acontece: a recursão passa pelo ambiente `ρ'` capturado pelo closure, e
> nenhuma ligação posterior altera `ρ'`. O comportamento do Python só é
> possível porque o escopo é **mutável**, o que é tema da Unidade 5.
> </details>

**Por que `letrec`, e não `def`?** O nome `letrec` deixa à vista a característica
que motiva e define a construção: a **recursão** (_rec_). Em `def`, a recursão
parece um efeito colateral do mecanismo de nomes; aqui, ela é o propósito.

#### Adicionando `def` como açúcar sintático

Nada impede de oferecermos, na superfície da linguagem, uma sintaxe mais próxima
de `def`, caso queiramos. Por exemplo, podemos querer escrever algo do tipo:

```text
def fat(n) =>
    if n == 0 then 1 else n * fat(n - 1)
in
fat(5)
```

O `in e₂` continua necessário porque `aljabr` é uma linguagem de expressões:
não há sequência de comandos em que `def` seria seguido de outras linhas
(isso só virá com a Unidade 5 e a Unidade 6). De fato, no código acima eu
dividi em linhas, apenas aproveitando o fato de que o léxico e o sintático
ignoram completamente os `\n`. O programa acima é uma expressão apenas:

```
def fat(n) => if n == 0 then 1 else n * fat(n - 1) in fat(5)
```

Mas a introdução das linhas e do açucar sintático de `def` tornam a linguagem
claramente mais _palatável_ para o programador.

A introdução de `def` nessa forma, contudo, pode ser feito apenas com o que
chamamos de **açúcar sintático** (_syntactic sugar_). A ideia é que a construção
ganha significado por **tradução** para uma construção que já existe. E isso 
pode ser (e muitas vezes é) feito diretamente no interpretador.

```text
def f(p₁, …, pₙ) => e₁ in e₂      ⟹      letrec f = fn (p₁, …, pₙ) => e₁ in e₂
```

Consequências:

- **nenhuma regra semântica nova**: `(LetRec)` já diz tudo o que `def` significa;
- **o avaliador não muda**: só o léxico (`def` passa a ser a oitava palavra
  reservada) e a sintaxe (uma alternativa a mais em `exp`). Esse tipo de
  tradução é chamado de _desugaring_.

Há mais de um lugar para fazer a tradução, todos sem tocar no avaliador:

| Onde                                   | Como                                                                                      | Avaliação                                                                 |
|----------------------------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| **No parser (na AST)**                 | `parse_def` já devolve `LetRec(f, Lambda(params, e₁), e₂)`                                | **a melhor opção**: a gramática continua sendo a autoridade sobre a sintaxe |
| Em um passe AST → AST                  | o parser devolve um nó `Def`; um passe separado o substitui por `LetRec` antes do `eval`  | boa, e deixa a AST de superfície disponível para mensagens de erro        |
| Nos tokens (pré-processamento do lexer)| troca `DEF NOME LPAREN` por `LETREC NOME EQUAL FN LPAREN`                                 | funciona, mas é frágil: erros sintáticos referem-se ao programa **traduzido**, não ao que o programador escreveu |

A ideia importante é a separação entre **núcleo** e **formas derivadas**. A
semântica formal só precisa cobrir o núcleo; o resto se explica por tradução.
Quanto menor o núcleo, menores a especificação e o interpretador (e, na
Unidade 8, o verificador de tipos).

Curiosidade: em `aljabr`, o próprio `let` também é açúcar, já que `let x = e₁
in e₂` e `(fn (x) => e₂)(e₁)` têm exatamente o mesmo significado (confira com as
regras `(Let)` e `(App)`). Já o `if` **não** pode ser açúcar: sua regra só
avalia um dos caminhos, e, com condição numérica, nenhuma das outras
construções consegue imitar isso.

## Bloco 6: Transparência referencial e linguagem funcional pura (≈ 15 min)

### 6.1 Transparência referencial

> Uma expressão é **referencialmente transparente** quando pode ser
> **substituída pelo seu valor** em qualquer ponto do programa sem alterar o
> significado do programa.

É a mesma ideia da álgebra do ensino médio: se `x = 2 + 3`, então `x * x`,
`5 * 5` e `(2 + 3) * (2 + 3)` são intercambiáveis. Em `aljabr`:

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

Consequências:

1. avaliar a mesma expressão duas vezes **sempre** dá o mesmo valor;
2. o valor de uma expressão depende **só** das subexpressões e do ambiente
   (isso é exatamente o **determinismo** + a **composicionalidade** que
   registramos nas Aulas 7, 8 e 12);
3. a ordem de avaliação de subexpressões independentes não altera o valor
   (ressalva fina: erro e não-terminação podem competir; não vamos explorá-la);
4. podemos raciocinar **equacionalmente**: substituir iguais por iguais.

> **Efeito colateral:** qualquer coisa observável de uma computação além do
> valor que ela produz. `aljabr` não tem nenhum: executar um programa só
> produz o seu valor.

### 6.2 Elo com substituição e ambiente

Na Aula 8, os dois modelos de `let` foram apresentados lado a lado:

- **por substituição:** `let x = 10 in (x - 1) * (x + 1)` vira `(10 - 1) * (10 + 1)`;
- **por ambiente:** mantemos `ρ = {x ↦ 10}` e consultamos quando preciso.

> **Pergunta:** por que dois modelos tão diferentes dão o **mesmo** resultado
> em `aljabr`?
> <details>
> <summary>Clique pra ver a resposta</summary>
>
> <br>Resposta: porque a linguagem é referencialmente transparente.
> Substituir um nome pelo seu valor é seguro justamente porque o valor nunca
> "muda por baixo". O modelo de ambiente é só a versão implementável do modelo
> de substituição (e evita o cuidado extra com captura de variáveis, que o
> closure resolve de graça).
> </details>

Volte ao Bloco 1: no escopo dinâmico, o significado de `f` depende do contexto
de chamada. Escopo dinâmico **ameaça** a transparência referencial; escopo
léxico a preserva.

> **Para guardar** (voltaremos a isso na Aula 15): o modelo de substituição só
> vale enquanto avaliar uma expressão não deixa efeito. Se algo puder mudar, o
> "valor de `x`" depende de **quando** perguntamos.

### 6.3 Nomear: linguagem funcional pura

> **Pergunta:** o que `aljabr` v3 tem? E o que ele **não** tem?
> <details>
> <summary>Clique pra ver a resposta</summary>
>
> | O que **introduzimos**                                  | O que **não** introduzimos                  |
> |---------------------------------------------------------|---------------------------------------------|
> | expressões (tudo produz valor, inclusive `if`)          | atribuição (`x := v`)                       |
> | funções como valores (primeira classe)                  | mutação de qualquer valor                   |
> | closures e escopo léxico                                | sequenciamento de comandos                  |
> | recursão como único mecanismo de repetição              | laços (`while`, `for`)                      |
> | transparência referencial                               | estado que muda ao longo do tempo           |
> |                                                         | efeitos colaterais                          |
> </details>

Agora podemos dar nome ao que construímos:

> `aljabr` é uma linguagem **funcional pura**. "Funcional" porque funções são
> valores e a computação é aplicação de funções; "pura" porque **não há
> efeitos**. O nome descreve um **conjunto de escolhas de design** e,
> principalmente, **o que abrimos mão**: a mutação.

Dois fechos:

- com `letrec`, `if` e aritmética, `aljabr` v3 é **Turing-completa** (e, com
  sintaxe infixa, é na prática o lambda cálculo);
- "funcional" não é propriedade de uma linguagem específica. Python, Java e
  JavaScript permitem **programar** em estilo funcional se o programador
  _escolher não usar_ certas features. Retomaremos isso na síntese
  (Unidade 9).


## Bloco 7: Tabela de síntese (início) (≈ 8 min)

A tabela completa fica no arquivo `tabela-design.md`, atualizado ao final de
cada unidade. Linhas: linguagens-objeto; colunas: dimensões de design. Abaixo,
o estado atual.

| Linguagem   | Avaliação                  | Vinculação        | Escopo                     | Abstração           | Estado | Dados                          | Controle                      | Tipos   |
|-------------|----------------------------|-------------------|----------------------------|---------------------|--------|--------------------------------|-------------------------------|---------|
| `rpn`       | pilha, estrita             | —                 | —                          | —                   | —      | números                        | sequência de tokens           | dinâmicos |
| `mlisp`     | recursiva sobre a AST      | —                 | —                          | —                   | —      | números                        | composição de expressões      | dinâmicos |
| `calc`      | recursiva sobre a AST      | —                 | —                          | —                   | —      | números                        | composição de expressões      | dinâmicos |
| `aljabr` v1 | por ambiente, estrita      | `let` (não rec.)  | léxico                     | valores nomeados    | —      | números                        | —                             | dinâmicos |
| `aljabr` v2 | por ambiente, estrita      | `let` (não rec.)  | léxico (closure)           | **computações**     | —      | números + closures             | —                             | dinâmicos |
| `aljabr` v3 | estrita, **exceto `if`**   | `let`, `letrec`   | léxico                     | funções recursivas  | —      | números + closures             | `if` (expressão), recursão    | dinâmicos (`2 + (1<2)` vale `3`) |

Colunas ainda **sem conteúdo** ("ainda não temos"): estado, dados compostos
(só números e closures) e tipos estáticos.

Para discutir:

- **avaliação de v3:** estrita _exceto_ `if`, que é uma forma especial;
- **dados:** closures são dados (os booleans da biblioteca são dados
  codificados como funções);
- **tipos:** a nota sobre números e "booleans" é a semente da Unidade 8.

**Tarefa opcional (Classroom):** escolha **uma célula** da tabela e justifique
o seu conteúdo com um programa ou uma regra.


## Bloco 8: O que ainda não conseguimos escrever (≈ 12 min)

Com `letrec` e `if` temos repetição. Mas ela é de um tipo especial: cada
repetição é uma **nova chamada** com **novos valores**. Nunca a _mesma_
variável com valor diferente. Três desafios mostram onde isso nos limita.

### 8.1 Um contador

Escreva `contador` tal que chamadas sucessivas devolvam `1`, `2`, `3`:

```text
contador()      # 1
contador()      # 2
contador()      # 3
```

> **Pergunta:** é possível em `aljabr`? Tente com closures.
> <details>
> <summary>Clique pra ver a resposta</summary>
>
> <br>Resposta: não. O ambiente capturado por um closure é imutável. Pior: em
> `aljabr`, uma função chamada com os mesmos argumentos **sempre** devolve o
> mesmo valor. `contador()` não pode existir.
> </details>

### 8.2 Um `enquanto`

```text
enquanto (i < 10) corpo
```

> **Pergunta:** que sentido teria esse laço em `aljabr`?
> <details>
> <summary>Clique pra ver a resposta</summary>
>
> <br>Resposta: se nada muda, `i < 10` vale sempre o mesmo. Ou o laço não
> executa nenhuma vez, ou executa para sempre. Em `aljabr`, repetição **só**
> existe como recursão.
> </details>

### 8.3 Reavaliar uma expressão

Pela transparência referencial, o valor de uma expressão é sempre o mesmo.
Reavaliá-la seria desperdício (poderíamos até guardar e reaproveitar o
resultado).

> **Pergunta:** em que condições faria sentido avaliar a mesma expressão duas
> vezes?
> <details>
> <summary>Clique pra ver a resposta</summary>
>
> <br>Resposta: quando o valor pode depender de **quando** a avaliação
> acontece.
> </details>

### 8.4 O que vem a seguir

> Todo o curso até aqui foi sobre uma linguagem em que **quando** não importa.
> Na quarta, vamos perder essa propriedade de propósito, e ver o que se ganha
> e o que se paga.


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


## Para checar seu entendimento

- **Bloco 2:** você consegue listar as quatro propriedades de primeira classe
  usando exemplos dos próprios programas?
- **Bloco 3:** você consegue explicar, sem ajuda, por que `se(true, 1, 1/0)`
  vale `erro`? E por que `let f = fn (n) => f(n) in f(1)` também?
- **Bloco 4:** você consegue explicar por que `letrec` é preferível a mudar o
  `let` (o exemplo `let x = x + 1`)?
- **Bloco 5:** você enxerga, na **forma** das regras `(If…)`, que só um
  caminho é avaliado? E consegue dizer o que há de circular em `(LetRec)`?
- **Bloco 6:** você consegue definir transparência referencial com as suas
  palavras e explicar por que substituição e ambiente coincidem em `aljabr`?
- **Bloco 8:** você consegue argumentar que o contador **não pode** existir em
  `aljabr`, e não apenas que "é difícil"?
