from lark import Lark
from lark import tree
from lark import lexer

Tree = tree.Tree
Token = lexer.Token

# Needed:
# * Need to be able to have statement that is nothing but whitespace
# * clean up pragma to handle the different valid pragmas

grammar = """
start: statements
statements: statement | (statement NEWLINE | NEWLINE)+

VARIABLE_NAME: /[a-zA-Z_][a-zA-Z0-9_]*(\[[0-9]+\])?/
TYPE: ("a".."z" | "A".."Z" | "_") ("a".."z" | "A".."Z" | "_" | "0".."9")*
instance_variable_chain: VARIABLE_NAME ("." VARIABLE_NAME)+
variable: VARIABLE_NAME | instance_variable_chain
variable_assignment: variable " "* "=" " "* statement
variable_increment: variable " "* "++"
variable_coercion: variable " "+ "as" " "+ TYPE

OPERATOR: ("+" | "-" | "*" | "/")
value_manipulation: statement_no_space_no_value_manip (" "*  OPERATOR " "* statement_no_space_no_value_manip " "*)+

STRING_CONTENTS_DOUBLE: /([^\"])+/
STRING_CONTENTS_SINGLE: /([^'])+/
string: "\\\"" STRING_CONTENTS_DOUBLE? "\\\"" | "'" STRING_CONTENTS_SINGLE? "'"

NUMBER: "0".."9"+ ("." "0".."9"+)?

FALSE: "false"
TRUE: "true"
boolean.1: FALSE | TRUE

EQUALITY: "==" | ">=" |"<=" | "<" | ">" |"!="
condition: statement " "* EQUALITY " "* statement
if_stat: "if" " "+ condition
else_stat.1: "else"

for_array: "for" " "+ variable " "+ "as" " "+ variable
for_object: "for" " "+ variable " "+ "as" " "+ variable " "* ":" " "* variable 
for_statement: "for" " "+ statement_no_space " "* ";" " "* statement_no_space " "* ";" " "* statement_no_space
for_stat: for_array | for_object | for_statement

while_stat: "while" " "+ condition

class_stat: "class" " "+ variable (" "+ "extends" " "+ variable)?

param: "," " "* variable " "*
first_param: " "* variable " "*
function_name: " "+ variable
function_definition: "function" function_name? " "* "(" first_param? param* " "* ")"
call_function: variable " "* "("
end_call_function: ")"
call_function_one_line: variable " "* "()"
return_stmt.1: "return" " "+ statement_no_space

PRAGMA_NAME: ("a".."z" | "A".."Z")+
PRAGMA_VALUE: ("a".."z" | "A".."Z" | "." | "0".."9" | " " | ",")+
pragma: "#" " "* PRAGMA_NAME (" "+ PRAGMA_VALUE)?

array_start: "["
array_end: "]"

map_start: "{"
map_end: "}"
map_row: VARIABLE_NAME " "* ":" " "* statement_no_space
map_one_line: "{" " "* "}"

TAG_SELF_CLOSE: "/"
TAG_NAME: ("a".."z" | "A".."Z")+
jsx_tag_start: "<" TAG_NAME " "* TAG_SELF_CLOSE? " "* jsx_tag_end?
jsx_tag_end: TAG_SELF_CLOSE? ">"
jsx_end: "</" " "* TAG_NAME " "* ">"

SPACE: " "
TAB: "\\t"
spaces: SPACE | TAB
statement_no_space: (variable | variable_assignment | string | NUMBER | condition | if_stat | for_stat | variable_increment | variable_coercion | while_stat | class_stat | function_definition | call_function | end_call_function | array_start | array_end | map_start | map_end | map_row | jsx_tag_start | jsx_tag_end | jsx_end | value_manipulation | call_function_one_line | map_one_line | boolean)
statement_no_space_no_value_manip: (variable | variable_assignment | string | NUMBER | condition | if_stat | for_stat | variable_increment | variable_coercion | while_stat | class_stat | function_definition | call_function | end_call_function | array_start | array_end | map_start | map_end | map_row | jsx_tag_start | jsx_tag_end | jsx_end | call_function_one_line | map_one_line | boolean)
statement: spaces* (variable | variable_assignment | string | NUMBER | condition | if_stat | for_stat | variable_increment | variable_coercion | while_stat | class_stat | function_definition | call_function | end_call_function | pragma | array_start | array_end | map_start | map_end | map_row | jsx_tag_start | jsx_tag_end | jsx_end | return_stmt | value_manipulation | call_function_one_line | else_stat | map_one_line | boolean)
NEWLINE: "\\n"
"""

parser = Lark(grammar)

def parse_statement(statement):
    #return process_statement(statement)
    return parser.parse(statement)
    
START = "states/start";
VARIABLE_OR_METHOD = "states/variable_or_method"
VARIABLE_SET = "states/variable_set"
STRING_DOUBLE = "states/string_double"
STRING_SINGLE = "states/string_single"
    
def process_tokens(tokens):
    print("starting")
    statement = []
    
    state = START
    context = {}
        
    def close_statement():
        print("closing time!")
        if len(context) == 0:
            return
        
        tokens = context.get("children", None)
        if tokens:
            statements = [];
    
            while len(tokens) > 0:
                result = process_tokens(tokens)
                tokens = result['tokens']
                statements += result['statement']

            context['children'] = statements
            
        if context["type"] == "string":
            statement.append(Tree("string", [Token("STRING_CONTENTS_DOUBLE", context['string'])]))
        elif context['type'] == 'variable_assignment':
            statement.append(Tree("variable_assignment", [
                Tree("variable", [Token("VARIABLE_NAME", context['variable'])]),
                Tree("statement", statements),
            ]))
        else:
            raise Exception("Unknown type {}".format(context['type']))
    
    while len(tokens) > 0:
        token = tokens.pop(0);
        
        print("handle token {}: \"{}\"".format(state, token))
        
        if state == START:
            if token == "\"":
                state = STRING_DOUBLE
                context["string"] = ""
                context["type"] = "string"
                continue
            elif token == "'":
                state = STRING_SINGLE
                context["string"] = ""
                context["type"] = "string"
                continue
            elif token == " ":
                continue
            else:
                state = VARIABLE_OR_METHOD
                context["variable_or_method"] = token
                continue
        elif state == VARIABLE_OR_METHOD:
            if token == " ":
                # ignore
                continue
            elif token == "=":
                state = VARIABLE_SET
                context["variable"] = context['variable_or_method']
                context['children'] = []
                context['type'] = 'variable_assignment'
                continue
        elif state == VARIABLE_SET:
            if token == "\n":
                close_statement()
                state = START
                context = {}
                statement.append(Token("NEWLINE", "\n"))
            else:
                context['children'].append(token)
            continue
        elif state == STRING_DOUBLE:
            if token == "\"":
                close_statement()
                state = START
                context = {}
                #print("after reset! {}".format(context))
                continue
            else:
                context["string"] += token
                continue
        elif state == STRING_SINGLE:
            if token == "'":
                close_statement()
                state = START
                context = {}
                #print("after reset! {}".format(context))
                continue
            else:
                context["string"] += token
                continue

        raise Exception("Unexpected token {}".format(token))
    
    close_statement()
    
    print("result {}".format(statement))
    
    return {
        "tokens": tokens,
        "statement": statement,
    }
    
def process_statement(statement):
    tokens = []
    token = ""
    slash = False
    for char in statement:
        print(char)
        if slash:
            char = "\\" + char
            slash = False

        if char == " " or char == "\"" or char == "\n" or char == "'":
            if len(token) > 0:
                tokens.append(token)
                token = ""
            tokens.append(char)
        elif char == "\\":
            slash = True
        else:
            token += char
            
    if len(token) > 0:
        tokens.append(token)
            
    print(tokens)
    
    statements = [];
    
    while len(tokens) > 0:
        result = process_tokens(tokens)
        tokens = result['tokens']
        statements.append(Tree("statement", result['statement']))
        
    print(statements)
    
    return Tree("start", [Tree("statements", statements)])