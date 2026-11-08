import re
from tipos import Token, TokenType, Erro

# Palavras reservadas: mapeamento de lexema -> TokenType
# aljabr v2 (§1): há apenas três na linguagem: `let`, `in` e `fn`.
RESERVADAS = {
    "let": TokenType.LET,
    "in": TokenType.IN,
    "fn": TokenType.FN,
}

# Mapeamento de regras léxicas (Ordem prioritária)
#
# (Importante: a ordem em que são adicionados os tipos de tokens e os
# respectivos valores de regex importa! Perceba que a REGEX única é gerada
# considerando essa ordem; em geral, vamos querer tokens com múltiplos
# caracteres o início (evitando que prefixos apareçam antes, como `*` e `**`;
# depois os de caractere único; depois os longos como inteiros e/ou
# identificadores; e no final, colocamos o equivalente ao nosso SPACE, também
# chamado de SKIP; seguido do MISMATCH que é o "ralo" pra pegar qualquer coisa
# que não seja reconhecida antes)
# 
TOKEN_SPEC = [
    ("POW",      r"\*\*"),
    ("ADD",      r"\+"),
    ("SUB",      r"-"),
    ("MULT",     r"\*"),
    ("DIV",      r"/"),
    ("INPUT",    r"\?"),
    ("LPAREN",   r"\("),
    ("RPAREN",   r"\)"),
    # aljabr v2 (§1): ARROW (`=>`) deve vir ANTES de EQUAL (`=`), senão a
    # regex única casaria `=` e deixaria um `>` órfão como MISMATCH. É a
    # mesma razão pela qual `**` vem antes de `*`.
    ("ARROW",    r"=>"),
    ("EQUAL",    r"="),
    # aljabr v2 (§1): COMMA — separa os itens de params e de args
    ("COMMA",    r","),
    ("INTEIRO",  r"\d+"),
    ("NOME",     r"[a-z_][a-z0-9_]*"),
    ("SPACE",    r"[ \t\n\r]+"),
    ("MISMATCH", r"."),
]

# Compilação da Regex única unindo todos os grupos nomeados
TOKEN_REGEX = re.compile(
    "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
)

def tokenizador(programa: str) -> list[Token] | Erro:
    tokens: list[Token] = []
    
    for match in TOKEN_REGEX.finditer(programa):
        kind = match.lastgroup
        value = match.group()
        
        if kind == "SPACE":
            continue
        elif kind == "MISMATCH":
            return Erro(f"erro léxico: token desconhecido '{value}'")
        elif kind == "NOME" and value in RESERVADAS:
            tokens.append(Token(RESERVADAS[value], value))
        else:
            tokens.append(Token(TokenType[kind], value))
            
    return tokens
