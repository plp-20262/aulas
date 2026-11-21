from tipos import (
    Ast, Erro, monadic_error, Stream, Token, TokenType,
    Stmt, Expr, VarDecl, Assign, FunDecl, ExprStmt, While, FieldWrite,
    Num, Var, AnonFun, Call, BinaryOp, UnaryOp, IfExpr, Block,
    RecordLit, FieldRead,
    INTEIRO, NOME, VAR_NAME, VAR, FUNCTION, FN, IF, ELSE, WHILE,
    COLON, DOT, THIS,
    ASSIGN, EQUAL, EQEQ, LT, OPS_ADIT, OPS_MULT, POW,
    UNARIO, LPAREN, RPAREN, LBRACE, RBRACE, SEMICOLON, COMMA
)

@monadic_error
def parser(tokens: list[Token]) -> Block | Erro:
    stream = Stream(tokens)
    block = parse_bloco_corpo(stream)
    
    if isinstance(block, Erro):
        return block

    if stream.peek() is not None:
        return Erro(f"sintaxe: tokens não consumidos após fim do programa '{stream.peek().lexema}'")

    return block

@monadic_error
def parse_bloco_corpo(stream: Stream) -> Block | Erro:
    stmts: list[Stmt] = []

    while True:
        tok = stream.peek()

        if VAR(tok) or FUNCTION(tok) or WHILE(tok):
            stmt = parse_comando(stream)
            if isinstance(stmt, Erro): return stmt
            stmts.append(stmt)
            continue

        if VAR_NAME(tok):
            tok_nome = stream.next()
            eh_atribuicao = bool(ASSIGN(stream.peek()))
            stream.it = iter([tok_nome] + list(stream.it))   # devolve o token
            if eh_atribuicao:
                stmt = parse_comando(stream)
                if isinstance(stmt, Erro): return stmt
                stmts.append(stmt)
                continue

        # qualquer outra coisa deve ser uma expressão (ou `chamada DOT NOME := exp ;`)
        exp = parse_exp(stream)
        if isinstance(exp, Erro): return exp

        if isinstance(exp, FieldRead) and ASSIGN(stream.peek()):
            stream.next()   # consome ':='
            rhs = parse_exp(stream)
            if isinstance(rhs, Erro): return rhs
            if not SEMICOLON(stream.peek()):
                return Erro("sintaxe: esperava ';' após atribuição")
            stream.next()
            stmts.append(FieldWrite(exp.obj, exp.field, rhs))
            continue

        if SEMICOLON(stream.peek()):
            stream.next()
            stmts.append(ExprStmt(exp))
        else:
            return Block(stmts, exp)


@monadic_error
def parse_comando(stream: Stream) -> Stmt | Erro:
    tok = stream.peek()
    if VAR(tok):
        stream.next()
        var_tok = VAR_NAME(stream.peek())
        if not var_tok: return Erro("sintaxe: esperava nome após 'var'")
        stream.next()
        
        if not ASSIGN(stream.peek()): return Erro("sintaxe: esperava ':=' em declaração")
        stream.next()
        
        e = parse_exp(stream)
        if isinstance(e, Erro): return e
        
        if not SEMICOLON(stream.peek()): return Erro("sintaxe: esperava ';' após declaração")
        stream.next()
        
        return VarDecl(var_tok.lexema, e)

    if VAR_NAME(tok):
        var_tok = stream.next()
        stream.next()
        e = parse_exp(stream)
        if isinstance(e, Erro): return e
        
        if not SEMICOLON(stream.peek()): return Erro("sintaxe: esperava ';' após atribuição")
        stream.next()
        
        return Assign(var_tok.lexema, e)

    if FUNCTION(tok):
        stream.next()
        var_tok = NOME(stream.peek())
        if not var_tok: return Erro("sintaxe: esperava nome de função")
        stream.next()
        
        if not LPAREN(stream.peek()): return Erro("sintaxe: esperava '(' após nome da função")
        stream.next()
        
        params = []
        if not RPAREN(stream.peek()):
            params = parse_params(stream)
            if isinstance(params, Erro): return params
            
        if not RPAREN(stream.peek()): return Erro("sintaxe: esperava ')'")
        stream.next()
        
        body = parse_bloco_delimitado(stream)
        if isinstance(body, Erro): return body
        
        return FunDecl(var_tok.lexema, params, body)

    if WHILE(tok):
        stream.next()
        cond = parse_exp(stream)
        if isinstance(cond, Erro): return cond

        body = parse_bloco_cmd(stream)
        if isinstance(body, Erro): return body

        # while_cmd não é seguido de ';' (como func_decl)
        return While(cond, body)

    return Erro(f"sintaxe: comando inválido '{tok.lexema if tok else 'EOF'}'")

@monadic_error
def parse_bloco_delimitado(stream: Stream) -> Block | Erro:
    if not LBRACE(stream.peek()): return Erro("sintaxe: esperava '{'")
    stream.next()
    
    body = parse_bloco_corpo(stream)
    if isinstance(body, Erro): return body
    
    if not RBRACE(stream.peek()): return Erro("sintaxe: esperava '}' no fim do bloco")
    stream.next()
    return body

@monadic_error
def parse_bloco_cmd(stream: Stream) -> list[Stmt] | Erro:
    """bloco_cmd ::= LBRACE { comando } RBRACE   (corpo do while: sem expressão final)"""
    if not LBRACE(stream.peek()): return Erro("sintaxe: esperava '{' no corpo do 'while'")
    stream.next()

    stmts: list[Stmt] = []
    while not RBRACE(stream.peek()):
        if stream.peek() is None: return Erro("sintaxe: esperava '}' no fim do bloco")
        stmt = parse_item_cmd(stream)
        if isinstance(stmt, Erro): return stmt
        stmts.append(stmt)

    stream.next()   # consome '}'
    return stmts

@monadic_error
def parse_item_cmd(stream: Stream) -> Stmt | Erro:
    """comando ::= func_decl | var_decl ; | atribuicao ; | while_cmd | exp ;"""
    tok = stream.peek()

    if VAR(tok) or FUNCTION(tok) or WHILE(tok):
        return parse_comando(stream)

    if VAR_NAME(tok):
        tok_nome = stream.next()
        eh_atribuicao = bool(ASSIGN(stream.peek()))
        stream.it = iter([tok_nome] + list(stream.it))   # devolve o token
        if eh_atribuicao:
            return parse_comando(stream)

    # qualquer outra coisa deve ser `chamada DOT NOME := exp ;` ou `exp ;`
    exp = parse_exp(stream)
    if isinstance(exp, Erro): return exp
    if isinstance(exp, FieldRead) and ASSIGN(stream.peek()):
        stream.next()   # consome ':='
        rhs = parse_exp(stream)
        if isinstance(rhs, Erro): return rhs
        if not SEMICOLON(stream.peek()):
            return Erro("sintaxe: esperava ';' após atribuição")
        stream.next()
        return FieldWrite(exp.obj, exp.field, rhs)
    if not SEMICOLON(stream.peek()):
        return Erro("sintaxe: esperava ';' após expressão (o corpo do 'while' não tem expressão final)")
    stream.next()
    return ExprStmt(exp)

@monadic_error
def parse_exp(stream: Stream) -> Expr | Erro:
    tok = stream.peek()
    if IF(tok):
        stream.next()
        cond = parse_exp(stream)
        if isinstance(cond, Erro): return cond
        then_b = parse_bloco_delimitado(stream)
        if isinstance(then_b, Erro): return then_b
        
        if not ELSE(stream.peek()): return Erro("sintaxe: esperava 'else'")
        stream.next()
        
        else_b = parse_bloco_delimitado(stream)
        if isinstance(else_b, Erro): return else_b
        return IfExpr(cond, then_b, else_b)

    if FN(tok):
        stream.next()
        if not LPAREN(stream.peek()): return Erro("sintaxe: esperava '(' após 'fn'")
        stream.next()
        params = []
        if not RPAREN(stream.peek()):
            params = parse_params(stream)
            if isinstance(params, Erro): return params
        if not RPAREN(stream.peek()): return Erro("sintaxe: esperava ')'")
        stream.next()
        
        body = parse_bloco_delimitado(stream)
        if isinstance(body, Erro): return body
        return AnonFun(params, body)

    return parse_comp(stream)

@monadic_error
def parse_comp(stream: Stream) -> Expr | Erro:
    left = parse_soma(stream)
    if isinstance(left, Erro): return left
    
    if EQEQ(stream.peek()) or LT(stream.peek()):
        op = stream.next().lexema
        right = parse_soma(stream)
        if isinstance(right, Erro): return right
        return BinaryOp(op, left, right)
        
    return left

@monadic_error
def parse_soma(stream: Stream) -> Expr | Erro:
    term = parse_termo(stream)
    if isinstance(term, Erro): return term
    while OPS_ADIT(stream.peek()):
        op = stream.next().lexema
        term2 = parse_termo(stream)
        if isinstance(term2, Erro): return term2
        term = BinaryOp(op, term, term2)
    return term

@monadic_error
def parse_termo(stream: Stream) -> Expr | Erro:
    factor = parse_fator(stream)
    if isinstance(factor, Erro): return factor
    while OPS_MULT(stream.peek()):
        op = stream.next().lexema
        factor2 = parse_fator(stream)
        if isinstance(factor2, Erro): return factor2
        factor = BinaryOp(op, factor, factor2)
    return factor

@monadic_error
def parse_fator(stream: Stream) -> Expr | Erro:
    u = parse_unario(stream)
    if isinstance(u, Erro): return u
    if POW(stream.peek()):
        stream.next()
        f = parse_fator(stream)
        if isinstance(f, Erro): return f
        return BinaryOp("**", u, f)
    return u

@monadic_error
def parse_unario(stream: Stream) -> Expr | Erro:
    if UNARIO(stream.peek()):
        op = stream.next().lexema
        call = parse_chamada(stream)
        if isinstance(call, Erro): return call
        return UnaryOp(op, call)
    return parse_chamada(stream)

@monadic_error
def parse_chamada(stream: Stream) -> Expr | Erro:
    ast = parse_atomo(stream)
    if isinstance(ast, Erro): return ast

    while LPAREN(stream.peek()) or DOT(stream.peek()):
        if LPAREN(stream.peek()):
            stream.next()
            args = []
            if not RPAREN(stream.peek()):
                args = parse_args(stream)
                if isinstance(args, Erro): return args
            if not RPAREN(stream.peek()): return Erro("sintaxe: esperava ')'")
            stream.next()
            ast = Call(ast, args)
        else:   # DOT NOME
            stream.next()
            campo = NOME(stream.peek())
            if not campo: return Erro("sintaxe: esperava nome de campo após '.'")
            stream.next()
            ast = FieldRead(ast, campo.lexema)

    return ast

@monadic_error
def parse_atomo(stream: Stream) -> Expr | Erro:
    tok = stream.peek()
    if INTEIRO(tok):
        stream.next()
        return Num(int(tok.lexema))

    if VAR_NAME(tok):
        stream.next()
        return Var(tok.lexema)

    if LBRACE(tok):
        if eh_record_lit(stream):
            return parse_record_lit(stream)
        return parse_bloco_delimitado(stream)

    if LPAREN(tok):
        stream.next()
        e = parse_exp(stream)
        if isinstance(e, Erro): return e
        if not RPAREN(stream.peek()): return Erro("sintaxe: esperava ')'")
        stream.next()
        return e

    return Erro(f"sintaxe: token inesperado '{tok.lexema if tok else 'EOF'}'")

def eh_record_lit(stream: Stream) -> bool:
    """Desambigua '{' em posição de átomo (README §2.1):
    '{}' ou '{ NOME : ...' -> record_lit; caso contrário -> bloco.
    """
    tok_lbrace = stream.next()          # consome '{'
    tok1 = stream.peek()
    if RBRACE(tok1):                    # '{ }' -> record vazio
        stream.it = iter([tok_lbrace] + list(stream.it))
        return True
    if NOME(tok1):
        tok_nome = stream.next()
        eh_campo = bool(COLON(stream.peek()))
        stream.it = iter([tok_lbrace, tok_nome] + list(stream.it))
        return eh_campo
    stream.it = iter([tok_lbrace] + list(stream.it))
    return False

@monadic_error
def parse_record_lit(stream: Stream) -> RecordLit | Erro:
    """record_lit ::= LBRACE [ campos ] RBRACE"""
    if not LBRACE(stream.peek()): return Erro("sintaxe: esperava '{'")
    stream.next()

    fields: list[tuple[str, Expr]] = []
    if RBRACE(stream.peek()):
        stream.next()
        return RecordLit(fields)

    campo = parse_campo(stream)
    if isinstance(campo, Erro): return campo
    fields.append(campo)

    while COMMA(stream.peek()):
        stream.next()
        campo = parse_campo(stream)
        if isinstance(campo, Erro): return campo
        fields.append(campo)

    if not RBRACE(stream.peek()): return Erro("sintaxe: esperava '}' no fim do record")
    stream.next()
    return RecordLit(fields)

def parse_campo(stream: Stream) -> tuple[str, Expr] | Erro:
    """campo ::= NOME COLON exp"""
    tok = NOME(stream.peek())
    if not tok: return Erro("sintaxe: esperava nome de campo")
    stream.next()
    if not COLON(stream.peek()): return Erro("sintaxe: esperava ':' após nome de campo")
    stream.next()
    e = parse_exp(stream)
    if isinstance(e, Erro): return e
    return (tok.lexema, e)

def parse_params(stream: Stream) -> list[str] | Erro:
    tok = VAR_NAME(stream.peek())
    if not tok: return Erro("sintaxe: esperava parâmetro")
    stream.next()
    params = [tok.lexema]
    while COMMA(stream.peek()):
        stream.next()
        tok = VAR_NAME(stream.peek())
        if not tok: return Erro("sintaxe: esperava nome após ','")
        stream.next()
        params.append(tok.lexema)
    return params

def parse_args(stream: Stream) -> list[Expr] | Erro:
    first = parse_exp(stream)
    if isinstance(first, Erro): return first
    args = [first]
    while COMMA(stream.peek()):
        stream.next()
        e = parse_exp(stream)
        if isinstance(e, Erro): return e
        args.append(e)
    return args
