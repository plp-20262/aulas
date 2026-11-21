# Aula 18 — 18/nov — Unidade 7 (2/3): objetos em `algora`

> Antes do início desta aula, revisei a abordaem chamada Tipos
> Algébricos (TADs) de Dados que é mais comum em linguagens
> funcionais, para suporte à modelagem de dados compostos. Por
> esse motivo, a implementação de TADs demonstrada foi com a
> linguagem Aljabr v4 deixada no diretório da Aula 17.


Esta aula é sobre a abordagem que conhecemos como Orientação a
Objetos (OO). O objetivo da aula é demonstrar como a OO pode ser
vista como consequência direta da presença de closures, mutação e
o suporte a registros (_records_) nas linguagens de programação.

## Progressão de Algora v2 até Algora v2 com suporte a OO

```
def contador(v) {
    if v == 0 
        { 0 }
    else 
        { contador(v - 1) }
}
contador(100)
```

Ponto de partida: um contador recursivo como esse acima
(em Algora v2) não permite ser invocado de forma sucessiva
e controlada, como desejamos. Queremos poder invocar o
contador um certo número de vezes e, em qualquer
momento desse processo, consultar o valor naquele
instante. Claramente, precisamos de estado para
obtermos esse comportamento, já que uma mesma expressão
de consulta (que será a aplicação de uma função)
precisará poder retornar valores diferentes se invocada
em diferentes momentos. Vejamos como podemos obter esse
comportamento com Algora, a linguagem em que
adicionamos estado e mutação.

### Passo 1 — closure sobre variável (Aula 15)

```
def Contador() {
    var n := 0;
    fn () { n := n + 1; n }
}

var c1 := Contador();
c1();
c1();
c1();
c1()
```

Esta é uma primeira tentativa. Observe que a função tem o
"jeitão" geral de objeto e ao mesmo tempo opera como um método.
A função retém estado (porque é um closure), seu estado pode ser
alterável (pq é mutável, graças à separação de ambiente
e store) e pode ser controlado por sucessivas invocações. Além
disso, cada função tem sua própria "identidade" (se criarmos mais
de um closure com múltiplas invocações de Contador, cada um deles
terá seu próprio estado).

Contudo, esse objeto é claramente muito primitivo, já que ele
implementa, essencialmente, um único método. Vejamos como podemos
ir além.

> Breve demo da função, para relembrar os alunos. Na demo, mostrei como
> objetos têm sua própria identidade: i) criando múltiplos contadores e
> demonstrando como são independentes; e ii) fazendo uma atribuição do
> tipo `var c2 := c1;` em que introduzo um alias para um objeto
> existente; na demo, mostrei que são apenas dois nomes que "apontam"
> para a mesma localização do store.

### Passo 2 — dispatcher de closures

```
var inc := 0;
var dec := 1;
var get := 2;
var ERRO := fn () { 1/0 };

def Contador() {
    var n := 0;

    def INC() { n := n + 1; n }
    def DEC() { n := n - 1; n }
    def GET() { n }

    fn (mensagem) {                     # Contador retorna um dispatcher…
        if mensagem == inc { INC }
        else { if mensagem == dec { DEC } 
        else { if mensagem == get { GET } 
        else { ERRO() }}}
    }
}
```

Nesta versão introduzimos um nível a mais de indireção. Na versão
anterior de Contador, o objeto retornado era o próprio objeto e
único método. Nesta, Contador retorna um closure intermediário
que implementa um padrão conhecido como _dispatcher_. Trata-se de
uma função de alta ordem que retornará uma outra função/closure.
Leia o código do closure retornado por Contador(): é uma função
que "seleciona" um dos closures definidos anteriormente, a partir
da "mensagem". E esse outro closure selecionado é o "método"
propriamente dito.

```
var c1 := Contador();
var c2 := Contador();
c1(inc)();      # c1(inc) é o método INC definido em Contador; c1(inc)() invoca INC
c1(inc)();      # …
c1(inc)();      # invoca INC 3 vezes, atualizando o valor de `n`
c2(inc)();      # c2(inc) é o método INC, mas do closure/objeto c2
c1(get)() + c2(get)()
```

Com `Contador()` assim definida, o código acim se torna viável.
Veja como o "jeitão" agora é essencialmente a forma de codificar
com classes e objetos. As primeiras duas linhas criam
_instâncias_ e as demais interagem com os objetos criados,
enviando-lhes mensagens para acessar os métodos desejados e
invocá-los. 

> Demo da função. Requer explorar pequenas variações. Ressaltar a
> similaridade do código (principalmente do lado cliente) com código OO
> típico.

Dois problemas ainda são evidentes. Primeiro, a sintaxe é
incômoda: em vez de `c1.inc()` precisamos escrever `c1(inc)()`.
E, segundo, o código requer um boilerplate repetitivo para
implementar o seletor de métodos: ou seja, o _dispatch_ das
mensagens é feito manualmento pelo programador. Apesar disso, a
percepção de funcionamento e uso da função/closure que é
produzida por Contador já nos permite que a chamemos de "objeto".
Afinal, ele encapsula (ou enclausura) um dado ao qual o acesso é
limitado às funções definidas dentro do próprio código da
definição de Contador (os métodos), tal como uma classe
convencional na OO.

### Passo 3 — record como feixe de closures (estado ainda capturado)

Os dois passos anteriores definem a OO como um _design pattern_
em linguagens de programação que tenham suporte a closures e
estado com mutação. Nos falta apenas resolver os dois problemas
acima mencionados e, para isso, basta introduzirmos um único
elemento em nossa linguagem: o suporte à composição de dados na
forma de registros (os chamados _records_ ou _structs_).

Abaixo, o mesmo exemplo acima na versão v3 de Algora, em que
introduzimos o suporte a registros na linguagem. Neste caso, usamos o
registro como um "feixe" de closures (os métodos) que compartilham um
mesmo estado (o `n`, neste caso).

```
def Contador() {
  var obj := {};
  var n := 0;
  obj.inc := fn () { obj.n := obj.n + 1; obj.n };
  obj.get := fn () { obj.n };
  obj
}
```

Observe que a função `Contador()` acima descrita é essencialmente o
típico código de uma classe em linguagens OO convencionais. Há algumas
diferenças, contudo: 1) a linguagem não suporta o conceito de _classe_
como entidade de primeira classe, mas apenas como um _design pattern_
aindap com isso, o construtor da "classe" é implementado como uma função
(por isso usamos `def Contador()`). Pelo mesmo motivo, precisamos código
para criar e retornar explicitamente o registro/objeto (veja a primeira
e a última linha da função). O restante da função, contudo, tem o típico
estilo de construtores da OO: a segunda linha cria e inicializa uma
propriedade (`n := 0`) e a terceira e a quarta cria os dois métodos que
atuam sobre a propriedade (`inc := fn …` e `get := fn …`).

Observe que a notação usada torna evidente que um objeto é um tão
somente um registro que reúne closures que operam sobre um certo
conjunto de dados enclausurados. Também é importante observar que a
adição de registros à linguagem nos permitiu dispensar o uso do
_dispatcher_ para selecionar os métodos. A notação de acesso aos membros
do registro nos servirá de acesso aos métodos.

> IMPORTANTE: na aula, chamei a atenção para o fato de que `obj` é
> apenas um nome interno que corresponde ao `this` em Java ou ao `self`
> em Python. Aqui, contudo, ele é uma simples variável e não tem
> qualquer regra semântica especial associada, como `this` e `self`.

```
var c1 := Contador();
var c2 := Contador();
c1.inc();      # c1.inc é o método INC definido em Contador; c1.inc() invoca INC
c1.inc();      # …
c1.inc();      # invoca INC 3 vezes, atualizando o valor de `n`
c2.inc();      # c2.inc é o método INC, mas do closure/objeto c2
c1.get() + c2.get()
```

> Demo. Aqui vale a pena dedicar mais tempo.

É importante chamar a atenção aqui! Observe que as características
essenciais de objetos estão presentes no valor retornado por
`Contador()`: i) cada objeto tem identidade própria; ii) cada objeto
encapsula seus próprios dados; iii) cada objeto oferece uma "API" de
acesso aos dados encapsulados a que podemos chamar de "métodos".

E o código acima exibe perfeitamente o "jeitão" de linguagens OO. De
fato, muito provavelmente, é código válido em linguagens como JS e
Python (talvez com poucos ajustes de sintaxe).

### Especificação formal de Algora v3: adição de Registros

Ver e discutir arquivo de especificação e arquivo das diferenças entre a
versão v2 e v3.

## Conclusão

O principal propósito desta aula é tornar evidente a relação entre as
construções de linguagens de programação que estudamos e como elas podem
dar origem a um tipo de linguagem que costumamos considerar de uma
família (ou _paradigma_) completamente diferente de linguagens. Vimos
que as características essenciais da orientação a objetos correspondem à
confluência de três elementos: closures léxicos, estado com mutação e
registros. Os objetos assim definidos têm identidade própria, encapsulam
dados e estado e oferecem uma API na forma de métodos que têm acesso aos
dados encapsulados. Além disso, a linguagem permite expressá-los de
forma simples, com a notação mais popular da OO, chamada de _dot
notation_; permite expressar construtores e métodos usando os mesmos
elementos da linguagem.

Obviamente, há mais elementos ainda a serem incluídos se considerarmos
linguagens assumidamente OO, tais como herança, polimorfismo, dados
públicos e privados, classes como cidadãs de primeira classe
distinguíveis de funções simples, etc. Saiba, contudo, que com as
características presentes em Algora v3, todos esses elementos adicionais
são relativamente fáceis de reproduzir ou até de adicionar à linguagem.
Alguns deles como _design patterns_, outros como pequenos acréscimos à
linguagem. A linguagem Algora v3, portanto, pode ser considerada uma
linguagem de programação OO (razão pela qual, talvez merecesse já um
novo nome).


## Sequência da aula apresentada

1. revisão de construções de linguagem para modelagem de dados compostos
   - Tipos Algébricos de Dados (TAD)
   - registros e Orientação a Objetos (OO)

2. implementação de Aljabr v4 com suporte a TAD
   - exemplos de modelagem de dados com TAD em Aljabr v4

3. caracterização da OO como confluencia de…
   - closures e escopo léxico
   - estado e mutação
   - objetos expressos como registros (records)

4. discussão da sintaxe escolhida para evoluir Algora v3
   - objetos/registros com notação JS: `{ campo : expr, … }`
   - acesso a campos: `obj.campo`
   - mutação de campos: `obj.campo := expr`
   - como closures são dados (funções são cidadãs de 1a classe):
     - métodos como campos ligados a closures: `obj.metodo := fn (…) { … }`
   - graças a escopo léxico, métodos têm acesso privilegiado ao objeto


## Revisão da tabela de síntese

- reapresentar e revisar a tabela de síntese
- incluir suporte a modelagem de dados compostos


# Aspectos de que abri mão nesta aula em relação ao plano original

1. a classe como molde: acho que o modelo que apresentei faz mais
   sentido do ponto de vista de PLP; de fato, do ponto de vista da
   atividade de programar, ver "classes como moldes" faz sentido; do
   ponto de vista de Paradigmas de Linguagens de Programação, contudo,
   me parece mais apropriado que o aluno entenda como vários conceitos
   se agregam para formar as ideias que embasam a orientação a objetos;

2. aliasing: embora não tenha retomado e reforçado o conceito de
   aliasing nesta aula, o essencial foi dito: objetos têm identidade;
   além disso, na demo, o aliasing for mostrado explicitamente;

3. `this` (de Java e de JavaScript) e `self` (de Python) merecem uma atenção
   esppecial na retomada da Aula 19; vale a pena demonstrar como
   programas semelantes em Algora, Java e Python têm diferentes
   semânticas no mesmo tema;

4. faltou demonstrar como escrever com OO o tipo composto AST que foi
   demonstrado com tipos algébricos; outro tópico deixado para a
   retomada do assunto na Aula 19;

5. na retomada do assunto na Aula 19, reforçar os aspectos relevantes:
   a modelagem de dados compostos com OO permite agrupar estado,
   operações e identidade;

6. de fato, desisti de apresentar o assunto com uma LP baseada em
   classes; acho que o conceito central mais importante são objetos com
   identidade, estado próprio e, portanto, suporte à mutação; interação
   baseada em mensagens (chamadas de métodos), encapsulamento de dados e
   acesso restrito via métodos (closures). Com isso, o conceito de
   classe como molde perde importância e pode ser percebido como uma
   mera evolução conceitual da função construtora de objetos da natureza
   escolhida (uma forma de promover a função de mera construtora de
   objetos em uma especificação do "molde" dos objetos daquela
   classe; e a promoção da invocação da função construtora em processo
   de instanciação).

7. apesar disso, decidi manter o termo "classe" para explorar a
   familiaridade prévia dos alunos com o assunto; mas, sempre chamando a
   atenção para o fato de que a LP não tem classes; que classe é
   meramente um _design pattern_ que a LP suporta e que é a base para classes
   em LPs OO clássicas;
