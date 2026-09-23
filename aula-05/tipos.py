from dataclasses import dataclass

type Ast = int | str | list[Ast]

@dataclass(frozen=True)
class Erro:
    msg: str


def monadic_error(func):
    def wrapper(tokens, *args, **kwargs):
        if isinstance(tokens, Erro):
            return tokens
        return func(tokens, *args, **kwargs)
    return wrapper
