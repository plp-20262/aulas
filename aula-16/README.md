# Aula 16 — 11/Nov — Unidade 5 (2/3)

> Os tópicos originais desta aula eram aprofundar o entendimento da mudança de
> framework semântico (visto na Aula 15), a diferença entre linguagens
> orientadas a expressões e orientadas a comandos e a introdução de repetições
> com estado, tipo `while` > em Algora. Na prática, contudo, a aula foi
> "sequestrada" por discussões sobre dúvidas e exemplos logo após a introdução
> do novo framework semântico. Apesar disso, acredito que tenha sido bastante
> produtiva, já que me permitiu esclarecer várias dúvidas dos alunos sobre o
> tema.
>
> O conteúdo original da parte de Repetições com Estado se encontra no arquivo
> `README-repeticoes-com-estado.md` que iria usar nesta aula, mas que só
> apresentarei, brevemente, na Aula 17 (ver diretório dessa aula para ver
> conteúdo efetivamente visto).

1. mudança do _framework semântico_: 
   - de julgamentos na forma: $\langle e, \rho \rangle \Downarrow v$ 
   - para a forma: $\langle p, \rho, \sigma \rangle \Downarrow \langle v, \rho_1, \sigma_1 \rangle$  

2. tipos de comandos e como são avaliados
   - expressões (puras) só produzem valores: $\langle e, \rho, \sigma \rangle \Downarrow v$ 
   - comandos alteram a memória: $\langle d, \rho, \sigma \rangle \Downarrow \langle \rho_1, \sigma_1 \rangle$ 

3. linguagens orientadas a expressões vs orientadas a comandos
   - as linguagens rpn, calc, mlisp e aljabr são todas orientadas a expressões
   - algora é orientada a comandos
   - com comandos surgem o estado, a mutação e os efeitos colaterais

4. apresentação do projeto de Algora (apresentar spec completa da v1 +
   implementação e exemplos);

- [Implementação de Algora](algora-v1)
- [Manual da Linguagem](algora-v1/MANUAL.md)
- [Especificação da Linguagem](algora-v1/README.md)
