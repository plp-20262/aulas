# O alias de tipo abaixo permite usar simples strings como erros.
# Obviamente, isto impõe uma limitação: funções que recebam
# strings não podem receber erros, da mesma forma que funções que
# retornem strings não podem retornar erros.
type Erro = str

def monadic_error(func):
    def wrapper(tokens, *args, **kwargs):
        if isinstance(tokens, str):
            return tokens
        return func(tokens, *args, **kwargs)
    return wrapper
