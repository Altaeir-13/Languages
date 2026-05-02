import ply.lex as lex
import ply.yacc as yacc

# --- PARTE 1: LEXER (Analisador Léxico) ---
# Define os tokens (os "tijolos" da linguagem)
tokens = ('NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'LPAREN', 'RPAREN')

# Define como reconhecer cada token (Expressões Regulares)
t_PLUS    = r'\+'
t_MINUS   = r'-'
t_TIMES   = r'\*'
t_DIVIDE  = r'/'
t_LPAREN  = r'\('
t_RPAREN  = r'\)'

# Ignorar espaços em branco
t_ignore  = ' \t'

# Regra para números
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Tratamento de erro léxico
def t_error(t):
    print(f"Caractere ilegal: {t.value[0]}")
    t.lexer.skip(1)

# Constrói o lexer
lexer = lex.lex()

# --- PARTE 2: PARSER (Analisador Sintático LALR(1)) ---
# Aqui definimos a Gramática Livre de Contexto (BNF)

# Precedência de operadores (para resolver conflitos shift/reduce)
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
)

def p_expression_binop(p):
    '''expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression'''
    if p[2] == '+': p[0] = p[1] + p[3]
    elif p[2] == '-': p[0] = p[1] - p[3]
    elif p[2] == '*': p[0] = p[1] * p[3]
    elif p[2] == '/': p[0] = p[1] / p[3]

def p_expression_group(p):
    'expression : LPAREN expression RPAREN'
    p[0] = p[2]

def p_expression_number(p):
    'expression : NUMBER'
    p[0] = p[1]

def p_error(p):
    print("Erro de sintaxe!")

# Constrói o parser (Isso gera as tabelas LALR por baixo dos panos)
parser = yacc.yacc()

# --- PARTE 3: LOOP DE EXECUÇÃO ---
print("Calculadora LALR(1) - Digite uma conta (ex: 3 + 4 * 10)")
while True:
    try:
        s = input('calc > ')
    except EOFError:
        break
    if not s: continue
    result = parser.parse(s)
    print(result)