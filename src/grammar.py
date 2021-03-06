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
    return process_statement(statement)
    #return parser.parse(statement)
    
START = "states/start";
VARIABLE_OR_METHOD = "states/variable_or_method"
VARIABLE_SET = "states/variable_set"
STRING_DOUBLE = "states/string_double"
STRING_SINGLE = "states/string_single"
NUMBER_STATE = "states/number"
VARIABLE_ADD_OR_INCREMENT = "states/variable_add_or_increment"
VARIABLE_COERCION = "states/variable_coercion"
IF_STATEMENT = "states/if_statement"
VARIABLE_EQUALITY = "states/variable_equality"
FOR_STATEMENT = "states/for_statement"

NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

# turn to true for debug logs
LOG = True

def log(str):
    if LOG:
        print(str)
    
def process_tokens(tokens):
    log("starting with {}".format(tokens))
    statement = []
    
    state = START
    context = {}

    def process_children(context, var):
        tokens = context.get(var, None)
        if tokens:
            statements = [];
    
            backup_context = context.copy()
            while len(tokens) > 0:
                result = process_tokens(tokens)
                tokens = result['tokens']
                statements += result['statement']

            # remove any spaces - inner children don't care about spaces
            for item in statements:
                if item == Tree("spaces", [Token('SPACE', ' ')]):
                    statements.remove(item)

            context[var] = statements

    def children_as_variable_name(children_arr):
        if len(children_arr) == 1 and isinstance(children_arr[0], str):
            return [
                Tree('variable', [Token('VARIABLE_NAME', children_arr[0])])
            ]
        return children_array

        
    def close_statement():
        log("closing time! {}".format(context))
        if len(context) == 0:
            return
        
        process_children(context, "children")

        if "spaces" in context:
            for i in range(0, context['spaces']):
                statement.append(Tree("spaces", [Token('SPACE', ' ')]))
            
        if context["type"] == "string":
            statement.append(Tree("string", [Token("STRING_CONTENTS_DOUBLE", context['string'])]))
        elif context["type"] == "string_single":
            statement.append(Tree("string", [Token("STRING_CONTENTS_SINGLE", context['string'])]))
        elif context['type'] == 'variable_assignment':
            # if we only have one child statement and it's a string, make it a variable instead
            context['children'] = children_as_variable_name(context['children'])
            statement.append(Tree("variable_assignment", [
                Tree("variable", [Token("VARIABLE_NAME", context['variable'])]),
                Tree("statement", context['children']),
            ]))
        elif context["type"] == "number":
            statement.append(Token("NUMBER", context['number']))
        elif context['type'] == "variable_increment":
            if isinstance(context['variable'], str):
                statement.append(Tree("variable_increment", [
                    Tree("variable", [Token("VARIABLE_NAME", context['variable'])]),
                ]))
            else:
                statement.append(Tree("variable_increment", [
                    Tree("variable", [context['variable']]),
                ]))
        elif context['type'] == 'variable_or_method':
            # in this case we just kick it back up the tree, we have no idea what to do with it at this level
            statement.append(context['variable_or_method'])
        elif context['type'] == 'variable_coercion':
            statement.append(Tree('variable_coercion', [
                Tree("variable", [Token('VARIABLE_NAME', context['variable'])]),
                Token('TYPE', context['children'][0]),
            ]))
        elif context['type'] == 'variable_equality':
            equality_statement = Token("EQUALITY", context['equality_type'])
            if context['equality_type'] == "=":
                equality_statement = Token('EQUALITY', '==')
    
            tree_children = [
                Tree('statement', [
                    Tree("variable", [Token('VARIABLE_NAME', context['variable'])]),
                ]),
                equality_statement,
            ]
            if (isinstance(context['children'][0], str)):
                tree_children.append(Tree('statement', [
                        Tree("variable", [Token('VARIABLE_NAME', context['children'][0])]),
                ]))
            else:
                tree_children.append(Tree('statement', [
                    context['children'][0],
                ]))
            statement.append(Tree('condition', tree_children))
        elif context['type'] == 'if':
            statement.append(Tree('if_stat', context['children']))
        elif context['type'] == 'for_as':
            process_children(context,"children")
            process_children(context,"children2")
            children = children_as_variable_name(context['children'])
            children2 = children_as_variable_name(context['children2'])
            statement.append(Tree("for_stat", [
                Tree('for_array', children + children2)
            ]))
        elif context['type'] == 'for_object':
            process_children(context,"children")
            process_children(context,"children2")
            process_children(context,"children3")
            children = children_as_variable_name(context['children'])
            children2 = children_as_variable_name(context['children2'])
            children3 = children_as_variable_name(context['children3'])
            statement.append(Tree("for_stat", [
                Tree('for_object', children + children2 + children3)
            ]))
        else:
            raise Exception("Unknown statement type {}".format(context['type']))
    
    while len(tokens) > 0:
        token = tokens.pop(0);
        
        log("handle token {}: \"{}\"".format(state, token))
        
        if state == START:
            if token == "\"":
                state = STRING_DOUBLE
                context["string"] = ""
                context["type"] = "string"
                continue
            elif token == "'":
                state = STRING_SINGLE
                context["string"] = ""
                context["type"] = "string_single"
                continue
            elif token == " ":
                if "spaces" not in context.keys():
                    context["spaces"] = 0
                context['spaces'] += 1
                continue
            elif token == "\n":
                return {
                    "tokens": tokens,
                    "statement": statement,
                    "raw": [Token("NEWLINE", "\n")],
                }
            elif token == "if":
                state = IF_STATEMENT
                context["type"] = "if"
                context["children"] = []
                continue
            elif len(token) > 0 and token[0] in NUMBERS:
                state = NUMBER_STATE
                context["type"] = "number"
                context["number"] = token
                continue
            elif token == "for":
                state = FOR_STATEMENT
                context['type'] = 'for'
                context['children'] = []
                context['children2'] = []
                context['children3'] = []
                context['found_as'] = False
                context['found_colon'] = False
                continue
            else:
                state = VARIABLE_OR_METHOD
                context['type'] = 'variable_or_method'
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
            elif token == "+":
                state = VARIABLE_ADD_OR_INCREMENT
                context["variable"] = context['variable_or_method']
                continue
            elif token == "as":
                state = VARIABLE_COERCION
                context["variable"] = context['variable_or_method']
                context['children'] = []
                context['type'] = 'variable_coercion'
                continue
            elif token == ">":
                state = VARIABLE_EQUALITY
                context['type'] = 'variable_equality'
                context['equality_type'] = '>'
                context['children'] = []
                context['variable'] = context['variable_or_method']
                continue
            elif token == "<":
                state = VARIABLE_EQUALITY
                context['type'] = 'variable_equality'
                context['equality_type'] = '<'
                context['children'] = []
                context['variable'] = context['variable_or_method']
                continue
            elif token == "!":
                state = VARIABLE_EQUALITY
                context['type'] = 'variable_equality'
                context['equality_type'] = '!'
                context['children'] = []
                context['variable'] = context['variable_or_method']
                continue
        elif state == VARIABLE_SET:
            if token == "\n":
                close_statement()
                state = START
                context = {}
                tokens.insert(0, "\n")
                continue
            elif token == "=":
                if len(context['children']) == 0:
                    # this is not a variable set
                    state = VARIABLE_EQUALITY
                    context['type'] = 'variable_equality'
                    context['equality_type'] = '='
                    continue
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
        elif state == VARIABLE_ADD_OR_INCREMENT:
            if token == "+":
                context['type'] = 'variable_increment'
                close_statement()
                state = START
                context = {}
                continue
        elif state == VARIABLE_COERCION:
            if token == " ":
                # ignore
                continue
            else:
                context['children'].append(token)
                continue
        elif state == IF_STATEMENT:
            if token == " ":
                # ignore
                continue
            elif token == "\n":
                close_statement()
                state = START
                context = {}
                tokens.insert(0, "\n")
                continue
            else:
                context["children"].append(token)
                continue
        elif state == VARIABLE_EQUALITY:
            if token == " ":
                # ignore
                continue
            elif token == "=":
                context["equality_type"] = context["equality_type"] + token
                continue
            else:
                context["children"].append(token)
                continue
        elif state == FOR_STATEMENT:
            if token == " ":
                # ignore
                continue
            elif token == "as":
                context['type'] = "for_as"
                context['found_as'] = True
                continue
            elif token == ":" and context['found_as']:
                context['type'] = "for_object"
                context['found_colon'] = True
                continue
            else:
                if not context['found_as']:
                    context['children'].append(token)
                    continue
                elif not context['found_colon']:
                    context['children2'].append(token)
                    continue
                else:
                    context['children3'].append(token)
                    continue

        raise Exception("Unexpected token {} for state {}".format(token, state))
    
    close_statement()
    
    log("result {}".format(statement))
    
    return {
        "tokens": tokens,
        "statement": statement,
    }
    
def process_statement(statement):
    tokens = []
    token = ""
    slash = False
    for char in statement:
        #log(char)
        if slash:
            char = "\\" + char
            slash = False

        if char == " " or char == "\"" or char == "\n" or char == "'" or char == "=" or char == "+" or char == ":" or char == ";":
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
            
    log(tokens)
    
    statements = [];
    
    while len(tokens) > 0:
        result = process_tokens(tokens)
        tokens = result['tokens']
        log("done processing statements! Tokens left? {}".format(tokens))
        if result['statement'] is not None:
            statements.append(Tree("statement", result['statement']))

        if 'raw' in result.keys():
            statements += result['raw']
        
    log(statements)
    
    return Tree("start", [Tree("statements", statements)])