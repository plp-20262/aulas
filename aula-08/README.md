# Aula 08 — 04/Out — Estágio 3 (Semana 2)

## Retomando da aula (e do Estágio) anterior

Na aula passada, retomamos o foco em semântica. Formalizamos a especificação da
semântica de nossa segunda linguagem `calc`, usando semântica de avaliação (ou
semântica natural ou ainda semântica operacional de passo grande). 

Optamos por usar a notação $⟨e, ρ⟩ ⇓ v$, denominada um _julgamento_, que
expressa que o significado da expressão $e$, sob o ambiente $ρ$, é o valor $v$.
Vimos também que definimos como domínios semânticos (os conjuntos de dados
usados para expressar qualquer estado da computação) os conjuntos:
$\mathrm{Val}$ de valores que une os valores propriamente válidos dos domínios
de interesse adicionados ao valor de $\mathrm{erro}$; e $\mathrm{Env}$ o
conjunto de possíveis ambientes que, por sua vez, são mapas de nomes de
variáveis para valores.

Apresentamos as regras de avaliação na notação de lógica para dedução
natural conhecida por notação Gentzen em que temos premissas e conclusões,
tipicamentes expressas acima e abaixo de uma linha (com o nome da regra do lado
direito). Defimos cinco regras para uma versão simples de `calc`:
$\mathrm{Num}$, $\mathrm{Op}$, $\mathrm{DivZero}$, $\mathrm{ErrEsq}$ e
$\mathrm{ErrDir}$.

Por fim, vimos como essas regras podem ser interpretadas como especificações
quase que literais de uma função `eval()` recursiva. Razão pela qual a própria
função tem assinatura semelhante à dos julgamentos: `eval(ast: Ast, env:
Environment) -> Val`.

Em `aula-08/calc-v4` apresento uma pequena, e última, atualização de `calc`.
Adicionei operadores unários e uma função de _lift_ para evelar as operações
parciais do domínio para operações totais. Com isso, é possível reduzir as
regras de tratamento de erro. Revise a definição formal de `calc-v4` no
[README.md](calc-v4/README.md) do diretório de `calc-v4`.


## 8. Nossa próxima Linguagem: calc com variáveis

(`aljabr`?)
