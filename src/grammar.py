#from lark import Lark
#from lark import tree
#from lark import lexer

#Tree = tree.Tree
#Token = lexer.Token

class Tree:
    def __init__(self, name, children):
        self.name = name
        self.children = children

    def __eq__(self, obj):
        if not isinstance(obj, Tree):
            return False
        if self.name != obj.name:
            return False
            
        if len(self.children) != len(obj.children):
            return False

        for index in range(len(self.children)):
            child = self.children[index]
            other_child = obj.children[index]

            if child != other_child:
                return False
        return True

    def __str__(self):
        result = "Tree(\"" + self.name + "\", ["

        str_child = []
        for child in self.children:
            str_child.append(str(child))

        result += ", ".join(str_child) + "])"
        return result

    def __repr__(self):
        return str(self)

class Token:
    def __init__(self, name, value):
        self.name = name
        self.value = value

        if not isinstance(self.value, str):
            raise Exception("Value to Token must be a string, got " + type(self.value).__name__)

    def __eq__(self, obj):
        if not isinstance(obj, Token):
            return False
        return self.name == obj.name and self.value == obj.value

    def __str__(self):
        result = "Token(\"" + self.name + "\", \"" + self.value + "\")"
        return result

    def __repr__(self):
        return str(self)


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

#parser = Lark(grammar)

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
VARIABLE_INCREMENT = "states/variable_increment"
VARIABLE_COERCION = "states/variable_coercion"
IF_STATEMENT = "states/if_statement"
VARIABLE_EQUALITY = "states/variable_equality"
FOR_STATEMENT = "states/for_statement"
WHILE_STATEMENT = "states/while_statement"
CLASS_STATEMENT = "states/class"
VARIABLE_CHAIN = 'states/variable_chain'
FUNCTION_DEFINITION = 'states/function_definition'
FUNCTION_CALL = "states/function_call"
PRAGMA = "states/pragma"
MAP_LINE = "states/map_line"
NEWLINE = "states/newline"

NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

# turn to true for debug logs
LOG = True

def log(str):
    if LOG:
        print(str)
    
"""def process_tokens(tokens, do_wrap=True):
    log("starting with {}".format(tokens))
    statement = []
    
    state = START
    context = {}

    def is_tree_with_spaces(tree):
        if not isinstance(tree, Tree):
            return False
        children = tree.children
        for child in children:
            if child != Tree("spaces", [Token('SPACE', ' ')]):
                return False
        return True

    def strip_spaces(statements):
        new_statements = []
        for item in statements:
            print('strip spaces ' + str(item))
            if not is_tree_with_spaces(item) and item != Tree("spaces", [Token('SPACE', ' ')]):
                print("is fine!")
                new_statements.append(item)
        return new_statements

    def process_children(context, var):
        tokens = context.get(var, None)

        if tokens:
            statements = []

            if len(tokens) == 1 and isinstance(tokens[0], Tree):
                return tokens[0]
    
            backup_context = context.copy()
            while len(tokens) > 0:
                result = process_tokens(tokens, False)
                tokens = result['tokens']
                statements += result['statement']
                log("added to children " + str(result['statement']))

            # remove any spaces - inner children don't care about spaces
            statements = strip_spaces(statements)
            context[var] = statements

    def children_as_variable_name(children_arr):
        if len(children_arr) == 1 and isinstance(children_arr[0], str):
            children = [
                Tree('variable', [Token('VARIABLE_NAME', children_arr[0])])
            ]
            return children
        return children_arr

    def wrap_in_statement(children, wrap_no_space_statement=False):
        if wrap_no_space_statement:
            return Tree("statement_no_space", children)
        
        return Tree("statement", children)

    def append_statement(statement, statements, wrap=True):
        if wrap and do_wrap:
            if not isinstance(statements, list):
                statements = [statements]
            statements = wrap_in_statement(statements)
        statement.append(statements)

    def unwrap_statements(data):
        result = []
        only_one = len(data) == 1
        for item in data:
            if isinstance(item, Tree) and item.name == "statement":
                result.append(item.children)
            else:
                result.append(item)
        if only_one and not isinstance(result[0], str):
            return result[0]
        return result
        
    def close_statement():
        results = process_statement(context)
        for result in results:
            if isinstance(result, list):
                for inner in result:
                    statement.append(inner)
            else:
                statement.append(result)

    def process_statement(context, keep_spaces=True):
        statement = []
        log("closing time! {}".format(context))
        if len(context) == 0:
            return statement
        
        process_children(context, "children")
        spaces = []

        def append(statements, wrap=True):
            if not isinstance(statements, list) and len(spaces) > 0:
                statements = spaces + [statements]
            elif isinstance(statements, list) and len(spaces) > 0:
                statements = spaces + statements
            append_statement(statement, statements, wrap)

        if "spaces" in context and keep_spaces:
            for item in context['spaces']:
                if item == 'space':
                    spaces.append(Tree("spaces", [Token('SPACE', ' ')]))
                elif item == 'tab':
                    spaces.append(Tree("spaces", [Token('TAB', '\t')]))
            
        if context["type"] == "string":
            append(Tree("string", [Token("STRING_CONTENTS_DOUBLE", context['string'])]))
        elif context["type"] == "string_single":
            append(Tree("string", [Token("STRING_CONTENTS_SINGLE", context['string'])]))
        elif context['type'] == 'variable_assignment':
            # if we only have one child statement and it's a string, make it a variable instead
            if len(context['children']) == 1 and context['children'][0] == '[':
                context['children'] = [Tree('array_start', [])]
            elif len(context['children']) == 1 and context['children'][0] == '{':
                context['children'] = [Tree('map_start', [])]
            else:
                context['children'] = children_as_variable_name(context['children'])
            context['variable'] = process_statement(context['variable'], False)
            context['variable'] = unwrap_statements(context['variable'])
            context['variable'] = children_as_variable_name(context['variable'])[0]
            append(Tree("variable_assignment", [
                context['variable'],
                Tree("statement", context['children']),
            ]))
        elif context["type"] == "number":
            append(Token("NUMBER", context['number']))
        elif context['type'] == "variable_increment":
            context['variable'] = process_statement(context['variable'], False)
            context['variable'] = children_as_variable_name(context['variable'])
            append(Tree("variable_increment", context['variable']))
        elif context['type'] == 'variable_or_method':
            if context['variable_or_method'] == ']':
                append(Tree("array_end", []))
            elif context['variable_or_method'] == '}':
                append(Tree("map_end", []))
            else:
                # in this case we just kick it back up the tree, we have no idea what to do with it at this level
                append(context['variable_or_method'], False)
        elif context['type'] == 'variable_coercion':
            context['variable'] = process_statement(context['variable'], False)
            context['variable'] = children_as_variable_name(context['variable'])
            append(Tree('variable_coercion', [
                context['variable'][0],
                Token('TYPE', context['children'][0]),
            ]))
        elif context['type'] == 'variable_equality':
            equality_statement = Token("EQUALITY", context['equality_type'])
            if context['equality_type'] == "=":
                equality_statement = Token('EQUALITY', '==')
    
            context['variable'] = process_statement(context['variable'], False)
            context['variable'] = children_as_variable_name(context['variable'])
            tree_children = [
                Tree('statement', context['variable']),
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
            append(Tree('condition', tree_children))
        elif context['type'] == 'if':
            append(Tree('if_stat', context['children']))
        elif context['type'] == 'for_as':
            process_children(context,"children")
            process_children(context,"children2")
            children = children_as_variable_name(context['children'])
            children2 = children_as_variable_name(context['children2'])
            append(Tree("for_stat", [
                Tree('for_array', children + children2)
            ]))
        elif context['type'] == 'for_object':
            process_children(context,"children")
            process_children(context,"children2")
            process_children(context,"children3")
            children = children_as_variable_name(context['children'])
            children2 = children_as_variable_name(context['children2'])
            children3 = children_as_variable_name(context['children3'])
            append(Tree("for_stat", [
                Tree('for_object', children + children2 + children3)
            ]))
        elif context['type'] == 'for':
            # our last children will be the final group before the statement ended
            context['child_list'].append(context['children'])
            context['children'] = context['child_list'][0]
            context['children2'] = context['child_list'][1]
            context['children3'] = context['child_list'][2]
            process_children(context,"children")
            process_children(context,"children2")
            process_children(context,"children3")
            children = children_as_variable_name(context['children'])
            children = wrap_in_statement(children, wrap_no_space_statement=True)
            children2 = children_as_variable_name(context['children2'])
            children2 = wrap_in_statement(children2, wrap_no_space_statement=True)
            children3 = children_as_variable_name(context['children3'])
            children3 = wrap_in_statement(children3, wrap_no_space_statement=True)
            append(Tree("for_stat", [
                Tree("for_statement", [children, children2, children3])
            ]))
        elif context['type'] == 'while':
            append(Tree("while_stat", context['children']))
        elif context['type'] == 'class':
            if not context['found_extends']:
                append(Tree("class_stat", [
                    Tree('variable', [Token("VARIABLE_NAME", context['class_name'])]),
                ]))
            else:
                append(Tree("class_stat", [
                    Tree('variable', [Token("VARIABLE_NAME", context['class_name'])]),
                    Tree('variable', [Token("VARIABLE_NAME", context['class_extends'])]),
                ]))
        elif context['type'] == 'variable_chain':
            tree = []
            for item in context['variable']:
                if isinstance(item, dict):
                    item = process_statement(item)
                    if len(item) == 1 and isinstance(item[0], str):
                        tree.append(Token("VARIABLE_NAME", item[0]))
                    else:
                        tree += item
                elif isinstance(item, str):
                    tree.append(Token("VARIABLE_NAME", item))
            
            append(Tree("variable", [Tree("instance_variable_chain", tree)]))
        elif context['type'] == 'function_definition':
            params = []
 
            for param in context["params"]:
                variable = Tree("variable", [Token("VARIABLE_NAME", param)])
                if len(params) == 0:
                    params.append(Tree("first_param", [variable]))
                else:
                    params.append(Tree("param", [variable]))
            if context['name'] is None:
                append(Tree("function_definition", params))
            else:
                append(Tree("function_definition",
                    [Tree('function_name', [
                        Tree("variable", [Token("VARIABLE_NAME", context['name'])]),
                    ])] + params,
                ))
        elif context['type'] == 'function_call':
            new_children = []
            for tokens in context['params']:
                stmts = []
                while len(tokens) > 0:
                    result = process_tokens(tokens, False)
                    tokens = result['tokens']
                    #result = strip_spaces(result['statement'])
                    stmts += result['statement']
                new_children.append(stmts)
            context['params'] = new_children
            variable_params = []
            for params in context['params']:
                new_params = []
                for param in params:
                    new_params.append(children_as_variable_name([param])[0])
                variable_params.append(new_params)
            append(Tree("call_function", [
                Tree("variable", [Token("VARIABLE_NAME", context['function'])]),
            ]))
            append(Token("NEWLINE", "\n"), False)
            for param_list in variable_params:
                append(param_list)
                append(Token("NEWLINE", "\n"), False)
            append(Tree("end_call_function", []))
        elif context['type'] == PRAGMA:
            children = [
                Token("PRAGMA_NAME", context['name']),
            ]
            if len(context['value']) > 0:
                value = "".join(context['value']).strip()
                # dumb thing to keep in line with the lark processor
                value = " " + value
                children.append(Token("PRAGMA_VALUE", value))
            append(Tree("pragma", children))
        elif context['type'] == MAP_LINE:
            context['children'] = wrap_in_statement(context['children'], True)
            append(Tree("map_row", [
                Token("VARIABLE_NAME", context['variable']),
                context['children']
            ]))
        else:
            raise Exception("Unknown statement type {}".format(context['type']))

        return statement

    def handle_equation(token, state, context):
        if token == "=":
            state = VARIABLE_SET
            context["variable"] = context.copy()
            context['children'] = []
            context['type'] = 'variable_assignment'
        elif token == "+":
            state = VARIABLE_ADD_OR_INCREMENT
            context["variable"] = context.copy()
        elif token == "as":
            state = VARIABLE_COERCION
            context["variable"] = context.copy()
            context['type'] = 'variable_coercion'
            context['children'] = []
        elif token == ">":
            state = VARIABLE_EQUALITY
            context['variable'] = context.copy()
            context['type'] = 'variable_equality'
            context['equality_type'] = '>'
            context['children'] = []
        elif token == "<":
            state = VARIABLE_EQUALITY
            context["variable"] = context.copy()
            context['type'] = 'variable_equality'
            context['equality_type'] = '<'
            context['children'] = []
        elif token == "!":
            state = VARIABLE_EQUALITY
            context["variable"] = context.copy()
            context['type'] = 'variable_equality'
            context['equality_type'] = '!'
            context['children'] = []
        elif token == ".":
            state = VARIABLE_CHAIN
            context["variable"] = [context.copy()]
            context['type'] = 'variable_chain'
            context['has_dot'] = True
        else:
            return None
        return (context, state)
    
    while len(tokens) > 0:
        token = tokens.pop(0)

        if isinstance(token, dict):
            context = token
            close_statement()
            continue
        
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
                    context["spaces"] = []
                context['spaces'].append('space')
                continue
            elif token == "\t":
                if "spaces" not in context.keys():
                    context["spaces"] = []
                context['spaces'].append('tab')
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
                context['child_list'] = []
                context['found_as'] = False
                context['found_colon'] = False
                continue
            elif token == "while":
                state = WHILE_STATEMENT
                context['type'] = 'while'
                context['children'] = []
                continue
            elif token == "class":
                state = CLASS_STATEMENT
                context['type'] = 'class'
                context['found_extends'] = False
                context['class_name'] = None
                context['class_extends'] = None
                continue
            elif token == "function":
                state = FUNCTION_DEFINITION
                context['type'] = 'function_definition'
                context['name'] = None
                context['in_params'] = False
                context['params'] = []
                context['found_param'] = False
                continue
            elif token == "#":
                state = PRAGMA
                context['type'] = PRAGMA
                context['name'] = None
                context['value'] = []
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
            elif token == "(":
                state = FUNCTION_CALL
                context['type'] = 'function_call'
                context['function'] = context['variable_or_method']
                context['temp_params'] = []
                context['params'] = []
                continue
            elif token in ["=", "+", "as", ">", "<", "!", "."]:
                result = handle_equation(token, state, context)
                if result != None:
                    (context, state) = result
                    continue
            elif token == '\n':
                close_statement()
                state = START
                context = {}
                tokens.insert(0, "\n")
                continue
            elif token == ":":
                state = MAP_LINE
                context['type'] = MAP_LINE
                context['variable'] = context['variable_or_method']
                context['children'] = []
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
            elif token == ";" and context['type'] == 'for':
                context['child_list'].append(context['children'])
                context['children'] = []
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
        elif state == WHILE_STATEMENT:
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
                context['children'].append(token)
                continue
        elif state == CLASS_STATEMENT:
            if token == " ":
                # ignore
                continue
            elif token == "\n":
                close_statement()
                state = START
                context = {}
                tokens.insert(0, "\n")
                continue
            elif token == "extends":
                context['found_extends'] = True
                continue
            else:
                if context['found_extends']:
                    context['class_extends'] = token
                else:
                    context['class_name'] = token
                continue
        elif state == VARIABLE_CHAIN:
            if token == '.':
                if not context['has_dot']:
                    context['has_dot'] = True
                    continue
            elif token == " ":
                continue
            elif token in ["=", "+", "as", ">", "<", "!", "."]:
                result = handle_equation(token, state, context)
                if result != None:
                    (context, state) = result
                    continue
            else:
                if context['has_dot']:
                    context['variable'].append(token)
                    context['has_dot'] = False
                    continue
        elif state == NUMBER_STATE:
            if token[0] in NUMBERS or token == ".":
                context['number'] += token
                continue
        elif state == FUNCTION_DEFINITION:
            if token == '(' and not context['in_params']:
                context['in_params'] = True
                continue
            elif token == ')' and context['in_params']:
                context['in_params'] = False
                context['found_param'] = False
                continue
            elif token == " ":
                continue
            elif context['in_params']:
                if token == ',':
                    if context['found_param']:
                        context['found_param'] = False
                        continue
                elif not context['found_param']:
                    context['params'].append(token)
                    context['found_param'] = True
                    continue
            elif not context['in_params']:
                context['name'] = token
                continue
        elif state == FUNCTION_CALL:
            if token == '\n':
                if len(context['temp_params']) > 0:
                    context['params'].append(context['temp_params'])
                    pass
                context['temp_params'] = []
                continue
            if token == ')':
                close_statement()
                state = START
                context = {}
                continue
            else:
                context['temp_params'].append(token)
                continue
        elif state == PRAGMA:
            if token == '\n':
                close_statement()
                state = START
                context = {}
                tokens.insert(0, "\n")
                continue
            else:
                if context['name'] == None:
                    if token == ' ':
                        continue
                    else:
                        context['name'] = token
                        continue
                else:
                    context['value'].append(token)
                    continue
        elif state == MAP_LINE:
            if token == '\n':
                close_statement()
                state = START
                context = {}
                tokens.insert(0, "\n")
                continue
            else:
                context['children'].append(token)
                continue
        raise Exception("Unexpected token \"{}\" for state {}".format(token, state))
    
    close_statement()
    
    log("result {}".format(statement))
    
    return {
        "tokens": tokens,
        "statement": statement,
    }"""
    
def process_statement(statement):
    tokens = []
    token = ""
    slash = False
    for char in statement:
        #log(char)
        if slash:
            char = "\\" + char
            slash = False

        if char == " " or char == "\"" or char == "\n" or char == "'" or char == "=" or char == "+" or char == ":" or char == ";" or char == "<" or char == ">" or char == "." or char == "(" or char == ")" or char == "," or char == "#" or char == "\t" or char == "[" or char == "]":
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
    
    statements = process_tokens2(tokens)
    trees = build_tree(statements)
    return Tree("start", [Tree("statements", trees)])

    """statements = []
    
    while len(tokens) > 0:
        result = process_tokens(tokens)
        tokens = result['tokens']
        log("done processing statements! Tokens left? {}".format(tokens))
        if result['statement'] is not None:
            statements += result['statement']

        if 'raw' in result.keys():
            statements += result['raw']
        
    log(statements)
    
    return Tree("start", [Tree("statements", statements)])"""

def process_tokens2(tokens):
    context_stack = []
    current_context = None

    statements = []

    line = 1

    def pop_context(newline=False):
        # if we have no context, then nothing to do
        if current_context == None:
            if newline:
                # if we have a newline we still want to insert it
                statements.append({"type": NEWLINE})
            return None

        # if we have no stack, then this is a top level statement so we just add
        # it to the list and reset the context
        if len(context_stack) == 0:
            statements.append(current_context)
            if newline:
                # top level statements care about newlines
                statements.append({"type": NEWLINE})
            return None
        parent = context_stack.pop()
        if "children" not in parent:
            parent["children"] = []
        parent["children"].append(current_context)
        return parent

    def pop_all_contexts():
        nonlocal current_context
        while len(context_stack) > 0:
            current_context = pop_context()
        # pop one last time to get the last statement appended
        pop_context()

    for token in tokens:
        state = (current_context['type'] if current_context is not None else None)
        log("handle token {}: \"{}\"".format(state, token))
        if token == "\n":
            line += 1
        if current_context == None:
            if token == " ":
                continue
            elif token == "\"":
                current_context = {
                    "type": STRING_DOUBLE,
                    "string": ""
                }
                continue
            elif token == "'":
                current_context = {
                    "type": STRING_SINGLE,
                    "string": ""
                }
                continue
            elif len(token) > 0 and token[0] in NUMBERS:
                current_context = {
                    "type": NUMBER_STATE,
                    "number": token
                }
                continue
            elif token == "if":
                current_context = {
                    "type": IF_STATEMENT,
                }
                continue
            elif token == "\n":
                statements.append({
                    "type": NEWLINE,
                })
                continue
            else:
                # default if it's not an operator or keyword, then it's probably a variable
                # or a function name
                current_context = {
                    "type": VARIABLE_OR_METHOD,
                    "variable": token
                }
                continue
        else:
            if current_context['type'] == VARIABLE_OR_METHOD:
                if token == " ":
                    continue
                elif token == "=":
                    current_context = {
                        "type": VARIABLE_SET,
                        "variable": current_context['variable'],
                    }
                    continue
                elif token == "+":
                    current_context = {
                        "type": VARIABLE_ADD_OR_INCREMENT,
                        "variable": current_context['variable'],
                    }
                    continue
                elif token == "as":
                    current_context = {
                        "type": VARIABLE_COERCION,
                        "variable": current_context['variable'],
                    }
                    continue
                elif token in ("<", ">", "!"):
                    current_context = {
                        "type": VARIABLE_EQUALITY,
                        "left_hand": [{
                            "type": VARIABLE_OR_METHOD,
                            "variable": current_context['variable'],
                        }],
                        "equality": token
                    }
                    continue
                elif token == "\n":
                    current_context = pop_context()
                    continue
            elif current_context['type'] == VARIABLE_SET:
                if token == " ":
                    continue
                elif token == "\n":
                    current_context = pop_context(True)
                    continue
                elif token == "=":
                    current_context = {
                        "type": VARIABLE_EQUALITY,
                        "left_hand": [{
                            "type": VARIABLE_OR_METHOD,
                            "variable": current_context['variable'],
                        }],
                        "equality": '=='
                    }
                    continue
                else:
                    tokens.insert(0, token)
                    context_stack.append(current_context)
                    current_context = None
                    continue
            elif current_context['type'] == STRING_DOUBLE:
                if token == "\"":
                    current_context = pop_context()
                    continue
                else:
                    current_context["string"] += token
                    continue
            elif current_context['type'] == VARIABLE_SET:
                if token == "\n":
                    current_context = pop_context(newline=True)
                    continue
            elif current_context['type'] == STRING_SINGLE:
                if token == "'":
                    current_context = pop_context()
                    continue
                else:
                    current_context["string"] += token
                    continue
            elif current_context['type'] == NUMBER_STATE:
                if token == '.' or len(token) > 0 and token[0] in NUMBERS:
                    current_context['number'] += token
                    continue
                else:
                    current_context = pop_context()
                    continue
            elif current_context['type'] == VARIABLE_ADD_OR_INCREMENT:
                if token == "+":
                    current_context = {
                        "type": VARIABLE_INCREMENT,
                        "variable": current_context['variable'],
                    }
                    current_context = pop_context()
                    continue
            elif current_context['type'] == VARIABLE_COERCION:
                if token == " ":
                    continue
                else:
                    current_context['new_type'] = token
                    current_context = pop_context()
                    continue
            elif current_context['type'] == IF_STATEMENT:
                if token == " ":
                    continue
                elif token == "\n":
                    tokens.insert(0, token)
                    current_context = pop_context()
                    continue
                else:
                    # handle condition, pushing token back onto the stack
                    tokens.insert(0, token)
                    context_stack.append(current_context)
                    current_context = None
                    continue
            elif current_context['type'] == VARIABLE_EQUALITY:
                if token == "=":
                    if len(current_context['equality']) < 2:
                        current_context['equality'] += token
                        continue
                elif token == "\n":
                    tokens.insert(0, token)
                    current_context = pop_context()
                    continue
                else:
                    tokens.insert(0, token)
                    context_stack.append(current_context)
                    current_context = None
                    continue
        
        raise Exception("Unexpected token at line " + str(line) + ": \"" + token + "\" " + state)

    # pop at the very end just to make sure we handle any final contexts
    pop_all_contexts()

    return statements

def build_tree(statements):
    tree_children = []

    def unwrap_statement(statement):
        if isinstance(statement, Tree) and statement.name == 'statement':
            return statement.children

        return statement

    for statement in statements:
        if statement['type'] == VARIABLE_SET:
            child = statement['children'][0]
            child_tree = build_tree([child])[0]

            tree_children.append(Tree("statement", [Tree("variable_assignment", [
                Tree("variable", [Token('VARIABLE_NAME', statement['variable'])]),
                child_tree,
            ])]))
        elif statement['type'] == STRING_DOUBLE:
            tree_children.append(Tree("statement", [Tree("string", [Token("STRING_CONTENTS_DOUBLE", statement['string'])])]))
        elif statement['type'] == STRING_SINGLE:
            tree_children.append(Tree("statement", [Tree("string", [Token("STRING_CONTENTS_SINGLE", statement['string'])])]))
        elif statement['type'] == NEWLINE:
            tree_children.append(Token("NEWLINE", "\n"))
        elif statement['type'] == NUMBER_STATE:
            tree_children.append(Tree('statement', [
                Token('NUMBER', statement['number']),
            ]))
        elif statement['type'] == VARIABLE_INCREMENT:
            tree_children.append(Tree('statement', [
                Tree('variable_increment', [
                    Tree("variable", [Token('VARIABLE_NAME', statement['variable'])]),
                ]),
            ]))
        elif statement['type'] == VARIABLE_COERCION:
            tree_children.append(Tree('statement', [
                Tree('variable_coercion', [
                    Tree("variable", [Token('VARIABLE_NAME', statement['variable'])]),
                    Token('TYPE', statement['new_type']),
                ]),
            ]))
        elif statement['type'] == IF_STATEMENT:
            child = statement['children'][0]
            child_tree = build_tree([child])[0]
            condition = build_tree([child])[0]
            condition_children = unwrap_statement(condition)
            condition = condition_children[0]

            tree_children.append(Tree('statement', [
                Tree('if_stat', [condition]),
            ]))
        elif statement['type'] == VARIABLE_EQUALITY:
            left_hand_trees = build_tree(statement['left_hand'])
            children = build_tree(statement['children'])
            result = left_hand_trees + [Token("EQUALITY", statement['equality'])] + children
            tree_children.append(Tree('statement', [Tree('condition', result)]))
        elif statement['type'] == VARIABLE_OR_METHOD:
            # if we got here it's clearly a variable
            tree_children.append(Tree('statement', [
                Tree("variable", [Token('VARIABLE_NAME', statement['variable'])])
            ]))
        else:
            raise Exception("build_tree: Unknown type " + statement['type'])

    return tree_children