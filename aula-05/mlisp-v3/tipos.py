from itertools import chain
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


class Stream:
    def __init__(self, tokens: list[str]):
        self.it = iter(tokens)

    def peek(self):
        try:
            valor = next(self.it)
        except StopIteration:
            return None
        self.it = chain((valor,), self.it)
        return valor

    def next(self):
        try:
            valor = next(self.it)
        except StopIteration:
            return None
        return valor

    def __iter__(self):
        return self.it
