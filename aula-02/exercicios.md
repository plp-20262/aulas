# Exercícios (Aula 02)

1. `[q05]` Tente fazer o interpretador `rpn2.py` quebrar. Escreva o arquivo
   `resposta.md` e   indique quais expressões quebram o interpretador. Explique
   quais motivos levam a isso. Como é possível corrigir? Reescreva `rpn.py`
   para que trate o caso em questão.

2. `[q06]` Um aspecto que deixamos por tratar, mas que mencionei em aula é que
   a adição dos dois novos operadores (`-` e `/`) e respectivas operações
   introduz tipos de dados resultantes que não podemos expressar em programas.
   Por exemplo, podemos escrever `1 2 /` e `1 2 -` que resultam,
   respectivamente, em `0.5` e `-1`. Mas nosso interpretador dará erro se esses
   mesmos dados forem fornecidos como entrada. Planeje uma mudança em nossa LP
   para que esses dados sejam aceitos e processados normalmente. Escreva quais
   as consequências dessas mudanças na LP?.

3. `[q07]` Escreva no arquivo `pb-spec.md` a especificação da LP notação
   polonesa (direta). Escreva uma seção para a específicação do léxico, outra
   para a sintaxe e outra para a semântica. Use expressões regulares, BNF e
   regras de transição.

4. `[q08]` Reescreva seu interpretador de notação polonesa (direta) `pn.py`,
   usando o mesmo estilo que usamos em nossa implementação de `rpn2.py`. Ou
   seja, deixe o lexer, o parser e o interpretador completamente independentes
   um do outro, usando um pipeline e tratamento monádico de erros.
