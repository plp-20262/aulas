import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lexer import tokenizador
from parser import parser
from algora import executar_programa, eval_expr
from tipos import Erro

@pytest.fixture
def env():
    return {}

def run_algora(prog: str):
    return executar_programa(prog, {}, {})
