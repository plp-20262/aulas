import pytest
from tipos import Erro, TNum, TBool, TFun
from verifica import verifica


class TestVerifica:
    """Fragmento da Aula 20 — tabela do §"Conjunto de testes" do
    README-church-v1.md (linhas 1191–1215)."""

    @pytest.mark.parametrize("code,expected", [
        ("42", TNum()),
        ("verdadeiro", TBool()),
        ("falso", TBool()),
        ("2 + 3 * 4", TNum()),
        ("-(2 ** 3)", TNum()),
        ("1 < 2", TBool()),
        ("2 == 2", TBool()),
        ("let x = 2 + 3 in x < 10", TBool()),
        ("let x = 1 in let x = x < 2 in x", TBool()),
        ("let a = 1 in let b = a + 1 in a * b", TNum()),
        ("let x = verdadeiro in 5", TNum()),
        ("1 / 0", TNum()),  # o verificador NÃO detecta divisão por zero
    ])
    def test_aceitos(self, parse, code, expected):
        ast = parse(code)
        assert not isinstance(ast, Erro)
        assert verifica(ast, {}) == expected

    @pytest.mark.parametrize("code,msg_substring", [
        ("2 + verdadeiro", "operador '+'"),
        ("(1 < 2) + 1", "operador '+'"),
        ("1 < verdadeiro", "operador '<'"),
        ("verdadeiro == verdadeiro", "operador '=='"),
        ("-verdadeiro", "operador '-'"),
        ("(1 < 2) < 3", "operador '<'"),
        ("x + 1", "não declarada"),
        ("(let x = 1 in x) + x", "não declarada"),
        ("let x = verdadeiro in x * 2", "operador '*'"),
    ])
    def test_rejeitados(self, parse, code, msg_substring):
        ast = parse(code)
        assert not isinstance(ast, Erro), f"esperava parse de {code!r}"
        result = verifica(ast, {})
        assert isinstance(result, Erro), f"esperava erro de tipo em {code!r}"
        assert msg_substring in result.msg


class TestVerificaFuncoes:
    """Regras da Aula 21: (T-Lam), (T-App), (T-If) e (T-LetRec)."""

    @pytest.mark.parametrize("code,expected", [
        ("fn (x: Num) => x + 1", TFun((TNum(),), TNum())),
        ("fn (x: Num, y: Num) => x < y", TFun((TNum(), TNum()), TBool())),
        ("fn (f: (Num) -> Num, x: Num) => f(f(x))",
         TFun((TFun((TNum(),), TNum()), TNum()), TNum())),
        ("fn () => 42", TFun((), TNum())),
        ("let dobro = fn (x: Num) => x * 2 in dobro(21)", TNum()),
        ("let twice = fn (f: (Num) -> Num) => fn (x: Num) => f(f(x)) in twice(fn (n: Num) => n + 1)(0)", TNum()),
        ("if verdadeiro then 1 else 2", TNum()),
        ("if 1 < 2 then 3 else 4", TNum()),
        ("letrec fat = fn (n: Num) : Num => if n == 0 then 1 else n * fat(n - 1) in fat(5)", TNum()),
    ])
    def test_aceitos(self, parse, code, expected):
        ast = parse(code)
        assert not isinstance(ast, Erro)
        assert verifica(ast, {}) == expected

    @pytest.mark.parametrize("code,msg_substring", [
        ("verdadeiro(1)", "não-função"),
        ("fn (x: Num) => x + verdadeiro", "operador '+'"),
        ("if 1 then 2 else 3", "condição de 'if'"),        # condição Num, não Bool
        ("if verdadeiro then 1 else verdadeiro", "ramos de 'if'"),
        ("let f = fn (x: Num) => x in f(1, 2)", "aridade"),
        ("let f = fn (x: Num) => x in f(verdadeiro)", "argumento"),
        ("letrec fat = fn (n: Num) : Bool => n in fat(1)", "tipo de retorno"),
    ])
    def test_rejeitados(self, parse, code, msg_substring):
        ast = parse(code)
        assert not isinstance(ast, Erro), f"esperava parse de {code!r}"
        result = verifica(ast, {})
        assert isinstance(result, Erro), f"esperava erro de tipo em {code!r}"
        assert msg_substring in result.msg
