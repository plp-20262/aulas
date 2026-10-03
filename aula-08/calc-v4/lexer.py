import re
from tipos import Token, TokenType, Erro

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
    ("INTEIRO",  r"\d+"),
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
        else:
            tokens.append(Token(TokenType[kind], value))
            
    return tokens
