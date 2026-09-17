# Aula 03

Tema da aula: sintaxe concreta X sintaxe abstrata.

Sintaxe concreta é o termo que usamos para nos referirmos ao
conjunto exato de caracteres, tokens e regras que são necessárias
para a escrita de frases válidas em uma dada linguagem de
programação.

No contexto de linguagens de programação, costumamos distinguir
sintaxe concreta e sintaxe abstrata. Em essência, a primeira se
refere às regras que determinam como um programa válido pode ser
escrito (incluindo nisso todos os caracteres e tokens
necessários) enquanto a segunda se refere a uma representação
mais pura da organização do que o programa expressa. A primeira
se aproxima mais ao texto e constuma ser representada na forma de
uma estrutura contendo todos os tokens visíveis no programa fonte
(uma lista de tokens, por exemplo). A segunda dispensa parte dos
tokens e se aproxima das necessidades de execução e/ou compilação
do programa; razão pela qual costuma ser uma estrutura que
representa apenas os elementos necessários à interpretação (ASTs,
tipicamente).

### AST (Árvore de Sintaxe Abstrata)

Nossa LP da aula anterior (RPN) exige que escrevamos as
expressões em notação posfixa. O ideal, claro, é que possamos
escrevê-las em notação infixa, tornando nossa LP mais apropriada
para uso humano. 

Considere as expressões `1 2 +` e `1 2 3 * +` (escritas em RPN) e
as expressões correspondentes em notação infixa `1 + 2` e `1 + (2
3)`, respectivamente. Embora a sintaxe concreta seja
evidentemente diferente nas duas linguagens, sabemos que as
expressões compartilham a semântica (o significado das expressões
é, por sinal, `3` e `7`, respectivamente).

Curiosamente, além da semântica, também podemos usar uma mesma
representação abstrata para a sintaxe nas duas linguagens. Esse
é, por sinal, o papel da chamada sintaxe abstrata: evidenciar a
estrutura do programa mais em termos da computação que expressa do
que da sintaxe concreta usada para escrever o programa.

Na prática, representarmos a sintaxe abstrata através de
ASTs (_Abstract Syntax Trees_). Abaixo, expresso da melhor forma
que me é possível em texto, as árvores sintáticas das duas
expressões acima. Acredito que sejam de fácil interpretação, após
nossa aula de hoje.

```
    +                          +
   / \                        / \
  1   2                      /   \
                            1     *
                                 / \
                                2   3
```

Mas como essas árvores podem ter sido derivadas as sintaxes
concretas mencionadas acima? Acredito que seja fácil de
relacionar as árvores com a notação infixa. Cada nó interno da
árvore tem um operador e, convenientemente, é desenhado entre (e
acima) dos nós filhos e fica fácil perceber que esses filhos são
os operandos daquele operador. Por isso, que na árvore à
esquerda, vemos o `+` na raiz e os operandos `1` e `2` nos nós
folhas. Claramente, isso expressa a operação que deve ser feita:
a soma de `1` e `2`. A mesma interpretação é dada para a árvore
do lado direito: cada nó interno tem operações `+` e `*`; e os
nós folha contêm valores literais `1`, `2` e `3`.

Um aspecto importante a perceber acima: observe que os tokens `(`
e `)` simplesmente não são necessários nas árvores, porque o que
eles expressam (ordem das operações) fica implícito pela
estrutura da árvore. Na árvore acima, fica claro que a operação
`*` entre `2` e `3` deve ser feita antes da operação `+`, pela
relação hierárquica dos nós.

### Relação das ASTs com as sintaxes concretas

Mas qual a relação das ASTs acima com as expressões nas sintaxes
concretas em RPN e em notação infixa? Para ver a relação, produza
a listagem dos nós, usando os caminhamentos clássicos em árvores:
em-ordem, pós-ordem e pré-ordem.

**Caminhamento em-ordem** O algoritmo de caminhamento em ordem
nas ASTs acima permite reconstruir as expressões originais
infixas. É preciso lembrar que, neste caso, é necessário
adicionar de volta os parênteses, considerando a hierarquia das
operações na árvore (operações mais perto da raiz são sempre
executadas depois).

**Caminhamento pós-ordem** Ao produzir o caminhamento em
pós-ordem nas ASTs, você vai obter as expressões em RPN. Confira
você mesmo e tente entender o motivo.

**Caminhamento pré-ordem** Além dos dois caminhamentos acima, há
também o caminhamento em pré-ordem… a esta altura, você não se
surpreenderá que isso produzirá as expressões em notação polonesa
direta (ou notação prefixa).

> Em geral, contudo, ao construirmos interpretadores, o que
> queremos é o caminho inverso: queremos partir da sintaxe
> concreta e produzir uma representação abstrata. Veremos isso a
> seguir.

### Relação das ASTs com a semântica

Observe que ASTs são excelentes estruturas de dados para a
análise semântica. Um interpretador extremamente simples pode ser
criado em estilo recursivo, explorando a natureza recursiva da
árvore. O pseudo-código é dado abaixo:

```
função interpretador(no_ast: Ast) → número | Erro:
    se no_ast é folha:
        retorna no_ast

    se no_ast é interno:
      operador = no_ast[0]
      arg1 = interpretador(no_ast[1])
      arg2 = interpretador(no_ast[2])
      op = OPERACAO[operador]
      retorna op(arg1, arg2)
```

A simplicidade desse pseudo-código dá noção da relação de
proximidade que uma AST guarda ao mesmo tempo com a sintaxe
concreta e com a semântica da LP.


## Lisp: s-expressões (ou notação prefixa parentizada)

Uma das LPs mais influentes de todos os tempos é Lisp (de fato,
talvez seja a LP mais influente já criada). Criada ainda em 1958,
quando a única LP existente era Fortran, Lisp introduziu uma
quantidade impressionante de novas ideias no mundo das LPs:
funções, recursividade, garbage collection, lambdas,
homoiconicidade, listas encadeadas, etc. Uma das ideias centrais
de Lisp é ser baseada em uma notação que até hoje é considerada
pouco convencional: s-expressões.

A notação de s-expressões é uma notação prefixa com uma única
diferença para a notação polonesa: exige o uso de parênteses ao
redor de cada aplicação de qualquer operação. Assim, em vez de
escrevermos `+ 1 2`, em Lisp, com s-expressões escrevemos: `(+ 1
2)`; em vez de `+ 1 * 2 3`, com s-expressões escrevemos `(+ 1 (*
2 3))`.

Uma das propriedades mais importantes dessa notação é que
dispensa qualquer regra de precedência, porque obriga o
programador a expressar de forma explícita a ordem em que quer
que as operações sejam executadas.

Outra propriedade importante é que a notação é praticamente uma
expressão linearizada da AST. Observe que cada par de parênteses
indica um nó interno da árvore. Por exemplo, a expressão `(+ 1 (*
2 3))` tem exatamente dois pares de parênteses, indicando dois
nós internos. Observe ainda que logo após cada parênteses de
abertura está a operação que deve ser colocada no nó interno. E
nos elementos seguintes estarão os argumentos da operação. Quando
os argumentos são inteiros, sabemos que na árvore se trata de um
nó folha. E se o argumento tem início com um novo parênteses, o
argumento será dado por uma sub-árvore. Confira isso nas árvores
e expressões acima.

### Da sintaxe concreta à abstrata de s-expressões

Para construírmos uma AST a partir da sintaxe concreta (sequência
de tokens) de um programa em s-expressões, podemos partir de um
algoritmo bastante conhecido: o algoritmo de pareamento de parênteses. 

Para parear parênteses, um algoritmo muito simples se baseia em
contagem. Cada vez que um token `(` é encontrado, incrementa-se a
variável de contagem. Quando um `)` é encontrado decrementamos a
variável, se for positiva; mas se for igual a zero, teremos
detectado uma sequência com falha no pareamento. Ao processar o
último token da entrada, se a variável de contagem for igual a
zero, o processo terá terminado com sucesso. Se terminar com
algum valor positivo, novamente teremos detectado um pareamento
com falha.

> Sugestão de exercício: faça o Exercício 1 da lista de
> exercícios fornecida nesta aula.

Uma variação um pouco mais sofisticada usa uma pilha em vez de um
contador. Essa pequena mudança permite parear corretamente
múltiplos tipos de delimitadores duplos (parênteses, colchetes,
chaves, etc). Em nosso caso, usaremos uma pilha porque nos
permitirá manter informação adicional, para construirmos a AST à
medida que processamos a sintaxe concreta (lista de tokens).

O algoritmo básico é bastante similar ao que descrevemos acima (o
ideal é que você tenha tentado o pequeno exercício acima, pra que
aqui você aproveite melhor o conteúdo abaixo). Abaixo segue o
pseudo-código que trata apenas s-expressões corretas…
obviamente, o papel fundamental de um parser é detectar programas
errados. No pseudo-código abaixo, ainda é necessário encaixar a
detecção de erros sintáticos em vários locais do código. Isso,
contudo, é algo que é mais fácil de fazer no código real, usando
casos de testes. Veja o exercício fornecido.

```
função parser(tokens: list[str]) → ast | Erro:
    para cada tok em tokens:
        se tok é '(':
            # criamos um novo nó (vazio) para a árvore…
            novo_nó: = [_, _, _]

            # …e colocamos na pilha até termos mais dados dele
            pilha.append(novo_nó)

        se tok é um número ou um operador:
            # adiciona tok ao nó do topo da pilha
            # é o nó que ainda está sendo feito, esperando o `)`
            último_nó = pilha[-1]
            último_nó.append(tok)

        se tok é ')':
            # agora fechamos o nó que está no topo da pilha
            último_nó = pilha.pop()
            se pilha ficou vazia:
                # o nó removido é o nó raiz da árvore
                ast = último_nó

            se a pilha não ficou vazia:
                # último_nó é parte do nó (agora) no topo
                pilha[-1].append(último_nó)

    retorna ast
```





