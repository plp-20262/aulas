# Aula 16 — 11/Nov — Unidade 5 (2/3)

Objetivo: evoluir no projeto de Algora (spec + implementação)

1. mudança do _framework semântico_: 
   - de julgamentos na forma: $\langle e, \rho \rangle \Downarrow v$ 
   - para a forma: $\langle p, \rho, \sigma \rangle \Downarrow \langle v, \rho_1, \sigma_1 \rangle$  

2. tipos de comandos e como são avaliados
   - expressões (puras) só produzem valores: $\langle e, \rho, \sigma \rangle \Downarrow v$ 
   - comandos alteram a memória: $\langle d, \rho, \sigma \rangle \Downarrow \langle \rho_1, \sigma_1 \rangle$ 

3. apresentação da implementação e exemplos

- [Implementação de Algora](algora-v1)
- [Manual da Linguagem](algora-v1/MANUAL.md)
- [Especificação da Linguagem](algora-v1/README.md)
