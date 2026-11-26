import pytest
from tipos import Erro, TNum, TBool, TFun


class TestTipoParser:
    """A nova categoria sintática `tipo` (§4.2).

    Como `parse` (fixture) lê uma expressão completa, embutimos o tipo numa
    anotação de parâmetro e conferimos a AST resultante.
    """

    @pytest.mark.parametrize("code,expected", [
        ("Num", TNum()),
        ("Bool", TBool()),
        ("(Num) -> Num", TFun((TNum(),), TNum())),
        ("(Num, Num) -> Bool", TFun((TNum(), TNum()), TBool())),
        ("() -> Num", TFun((), TNum())),
        # seta associativa à direita: (Num) -> ((Num) -> Num)
        ("(Num) -> (Num) -> Num", TFun((TNum(),), TFun((TNum(),), TNum()))),
        # parâmetro de tipo função
        ("((Num) -> Num, Num) -> Num",
         TFun((TFun((TNum(),), TNum()), TNum()), TNum())),
    ])
    def test_tipo(self, parse, code, expected):
        ast = parse(f"fn (x: {code}) => x")
        assert not isinstance(ast, Erro)
        assert ast == ["fn", [("x", expected)], "x"]


class TestChurchParserAccept:
    """Programas que o parser de church deve ACEITAR (§4.2)."""

    @pytest.mark.parametrize("code", [
        "fn () => 42",
        "fn (f: (Num) -> Num, x: Num) => f(f(x))",
        "fn (g: () -> Bool) => g()",
        "fn (x: Num) => fn (y: Num) => x + y",
        "letrec f = fn (n: Num) : (Num) -> Num => fn (m: Num) => n + m in f(1)(2)",
        "verdadeiro(1)",  # sintaticamente ok; erro de TIPO (verificador)
    ])
    def test_accept(self, parse, code):
        result = parse(code)
        assert not isinstance(result, Erro), f"esperava aceitar {code!r}, obteve {result!r}"


class TestChurchParserReject:
    """Programas que o parser de church deve REJEITAR (§4.2)."""

    @pytest.mark.parametrize("code", [
        "fn (x) => x",                 # parâmetro sem anotação
        "fn (x:) => x",                # falta o tipo
        "fn x: Num => x",              # faltam os parênteses dos parâmetros
        "fn (x: Num) : Num => x",      # fn comum não tem tipo de retorno
        "letrec f = fn (n: Num) => n in f(1)",  # letrec exige tipo de retorno
        "let x: Num = 1 in x",         # let não tem anotação
        "fn (f: Num -> Num) => f(1)",  # lista de parâmetros do tipo sem parênteses
        "fn (f: (Num) -> (Num)) => f(1)",  # depois da seta falta um tipo completo
        "fn (x: Foo) => x",            # Foo não é tipo (erro LÉXICO)
        "Num",                          # um tipo não é uma expressão
        "let verdadeiro = 1 in 2",     # palavra reservada
        "1 < 2 < 3",                    # comp não-associativa
    ])
    def test_reject(self, parse, code):
        result = parse(code)
        assert isinstance(result, Erro), f"esperava rejeitar {code!r}, obteve {result!r}"
