import string
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
    
START = "states/start"
END = "states/end"
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
FOR_AS = "states/for_as"
WHILE_STATEMENT = "states/while_statement"
CLASS_STATEMENT = "states/class"
VARIABLE_CHAIN = 'states/variable_chain'
FUNCTION_DEFINITION = 'states/function_definition'
FUNCTION_CALL = "states/function_call"
END_FUNCTION_CALL = "states/end_function_call"
PRAGMA = "states/pragma"
MAP_LINE = "states/map_line"
NEWLINE = "states/newline"
ARRAY_START = "states/array_start"
MAP_START = "states/map_start"
JSX = "states/jsx"
JSX_ATTRIBUTE = "states/jsx_attribute"
JSX_TAG_END = "states/jsx_tag_end"
RETURN = "states/return"
VARIABLE_MANIPULATE = "states/variable_manipulate"
ARRAY_OBJECT_INDEXING = "states/array_object_indexing"
BOOLEAN = "states/boolean"
ELSE_STATEMENT = "states/else_statement"
JSX_TEXT_CONTENT = "states/jsx_text_content"

# sub-states for JSX parsing
JSX_START = "jsx_states/start"
JSX_ATTRIBUTES = "jsx_states/attributes"
JSX_CHILDREN = "jsx_states/children"

NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
END_STATS = ["\n", ";"]
VALID_VARIABLE_START = list(string.ascii_lowercase) + list(string.ascii_uppercase) + ["_"]

# turn to true for debug logs
LOG = False

def log(str):
    if LOG:
        print(str)
    
    
def process_statement(statement):
    tokens = []
    token = ""
    slash = False
    for char in statement:
        #log(char)
        if slash:
            char = "\\" + char
            slash = False

        if char == " " or char == "\"" or char == "\n" or char == "'" or char == "=" or char == "+" or char == ":" or char == ";" or char == "<" or char == ">" or char == "." or char == "(" or char == ")" or char == "," or char == "#" or char == "\t" or char == "[" or char == "]" or char == "/" or char == "{" or char == "}":
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
    
    statements = process_tokens(tokens)
    trees = build_tree(statements)
    return Tree("start", [Tree("statements", trees)])

def process_tokens(tokens):
    context_stack = []
    current_context = {
        "type": START,
        "spaces": 0,
        "tabs": 0,
        "nested": 0,
    }

    statements = []

    line = 1

    def pop_context(newline=False):
        nonlocal current_context, line
        # if we have no context, then nothing to do
        if current_context['type'] == START:
            if newline:
                log("Appending a newline to statements")
                # if we have a newline we still want to insert it
                statements.append({"type": NEWLINE})
            if len(context_stack) > 0:
                # if we have something on the stack just move up without appending the child
                return context_stack.pop()

            return {
                "type": START,
                "spaces": 0,
                "tabs": 0,
                "nested": 0,
            }

        log("popping context " + str(len(context_stack)))
        # if we have no stack, then this is a top level statement so we just add
        # it to the list and reset the context
        if len(context_stack) == 0:
            log("Adding {} to statements".format(current_context['type']))
            statements.append(current_context)
            if newline:
                log("Appending a newline to statements")
                # top level statements care about newlines
                statements.append({"type": NEWLINE})
            return {
                "type": START,
                "spaces": 0,
                "tabs": 0,
                "nested": 0,
            }
        ###### TODO #########
        parent = context_stack.pop()
        if current_context['nested'] is not None:
            # start always owns everything
            parent_tabs = current_context['tabs'] > parent['tabs']
            parent_spaces = current_context['spaces'] > parent['spaces']
            if parent_tabs or parent_spaces or parent['type'] == START:
                log("Adding {} to nested parent ({}) tabs {} parent {}".format(current_context['type'], parent['type'], current_context['tabs'], parent['tabs']))
                if "nested_children" not in parent:
                    parent['nested_children'] = []
                parent['nested_children'].append(current_context)
            else:
                log("Context is not nested tabs {} parent {} of type {}".format(current_context['tabs'], parent['tabs'], parent['type']))
                # in this case we can assume the parent is done as well since we've found something not nested in it
                backup_context = current_context
                current_context = parent
                new_parent = pop_context()
                # this current context belongs on this parent as well. So push it back on the stack and re-pop our current context
                # but only if it's not the start, if it's start, then don't append
                if new_parent['type'] != START:
                    context_stack.append(new_parent)
                current_context = backup_context
                return pop_context()
        else:
            if "children" not in parent:
                parent["children"] = []
            parent["children"].append(current_context)
        return parent

    def pop_all_contexts():
        nonlocal current_context
        if current_context['type'] == START:
            # the only place it can go to None
            current_context = {
                "type": END,
                "nested": None,
            }
        while len(context_stack) > 0:
            current_context = pop_context()
        # pop one last time to get the last statement appended
        pop_context()

    def copy_context(new_context):
        new_context.update({
            "spaces": current_context['spaces'],
            "tabs": current_context['tabs'],
            "nested": current_context['nested'] if "nested" in current_context else False,
        })
        return new_context

    def remove_spaces(context):
        new_context = context.copy()
        new_context['spaces'] = 0
        new_context['tabs'] = 0
        return new_context

    def append_context_stack(getting_nested = False):
        nonlocal current_context
        log("Appending context " + current_context['type'] + " nested? " + str(getting_nested))
        context_stack.append(current_context)
        current_context = {
            "type": START,
            "spaces": 0,
            "tabs": 0,
            "nested": current_context['tabs'] if getting_nested else None,
        }

    for token in tokens:
        state = current_context['type']

        parent_state = None
        if len(context_stack) > 0:
            parent = context_stack[-1]
            parent_state = parent['type']

        log("handle token {}: \"{}\" ({}, {}) context stack: {}. Parent: {}".format(state, token, current_context['spaces'], current_context['tabs'], len(context_stack), parent_state))
        if token == "\n":
            line += 1

        # tokens that we handle a specific way based on parent
        if token == "]" and parent_state == ARRAY_OBJECT_INDEXING:
            tokens.insert(0, token)
            current_context = pop_context()
            continue
        elif token == "}" and parent_state == JSX_ATTRIBUTE:
            tokens.insert(0, token)
            current_context = pop_context()
            continue

        if current_context['type'] == START:
            if token == " ":
                current_context['spaces'] += 1
                continue
            elif token == "\t":
                current_context['tabs'] += 1
                continue
            elif token == "\"":
                current_context = copy_context({
                    "type": STRING_DOUBLE,
                    "string": ""
                })
                continue
            elif token == "'":
                current_context = copy_context({
                    "type": STRING_SINGLE,
                    "string": ""
                })
                continue
            elif len(token) > 0 and token[0] in NUMBERS:
                current_context = copy_context({
                    "type": NUMBER_STATE,
                    "number": token
                })
                continue
            elif token == "if":
                current_context = copy_context({
                    "type": IF_STATEMENT,
                })
                continue
            elif token == "\n":
                if parent_state is None:
                    log("Adding a newline from state machine")
                    statements.append({
                        "type": NEWLINE,
                    })
                continue
            elif token == "for":
                current_context = copy_context({
                    "type": FOR_STATEMENT,
                })
                continue
            elif token == "while":
                current_context = copy_context({
                    "type": WHILE_STATEMENT,
                })
                continue
            elif token == "class":
                current_context = copy_context({
                    "type": CLASS_STATEMENT,
                    "class": None,
                    "extends": None,
                })
                continue
            elif token == "function":
                current_context = copy_context({
                    "type": FUNCTION_DEFINITION,
                    "in_params": False,
                    'params': [],
                    "waiting_for_param": False,
                    "function_name": None,
                })
                continue
            elif token == ")":
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            elif token == "#":
                current_context = copy_context({
                    "type": PRAGMA,
                    "pragma_name": None,
                    "pragma_value": None,
                })
                continue
            elif token == "[":
                current_context = copy_context({
                    "type": ARRAY_START,
                    "buffer": [],
                    "last_newline": False,
                })
                continue
            elif token == "{":
                current_context = copy_context({
                    "type": MAP_START,
                    "has_key": False,
                    "last_newline": False,
                })
                continue
            elif token == "<":
                current_context = copy_context({
                    "type": JSX,
                    "self_close": False,
                    "end_tag": False,
                    "tag": None,
                    "substate": JSX_START,
                })
                continue
            elif token == "return":
                current_context = copy_context({
                    "type": RETURN
                })
                continue
            elif token == "false" or token == "true":
                current_context = copy_context({
                    "type": BOOLEAN,
                    "boolean": token,
                })
                continue
            elif token == "else":
                current_context = copy_context({
                    "type": ELSE_STATEMENT,
                    "condition": None,
                })
                continue
            elif token == "}":
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            # should always be at the very end
            elif len(token) > 0 and token[0] in VALID_VARIABLE_START:
                if parent_state == JSX:
                    # this is going to be regular text inside a JSX tag
                    current_context = copy_context({
                        "type": JSX_TEXT_CONTENT,
                        "text": token,
                    })
                    continue
                else:
                    # default if it's not an operator or keyword, then it's probably a variable
                    # or a function name
                    current_context = copy_context({
                        "type": VARIABLE_OR_METHOD,
                        "variable": token,
                        "has_data": False,
                    })
                    continue
        elif current_context['type'] == VARIABLE_OR_METHOD:
            if token == " ":
                continue
            elif token == "=":
                current_context = copy_context({
                    "type": VARIABLE_SET,
                    "left_hand": [remove_spaces(current_context)],
                })
                continue
            elif token == "+":
                current_context = copy_context({
                    "type": VARIABLE_ADD_OR_INCREMENT,
                    "variable": current_context['variable'],
                })
                continue
            elif token == "as":
                if parent_state == FOR_STATEMENT:
                    current_context = copy_context({
                        "type": FOR_AS,
                        "variable": current_context['variable'],
                        "is_object": False,
                    })
                else:
                    current_context = copy_context({
                        "type": VARIABLE_COERCION,
                        "variable": current_context['variable'],
                    })
                continue
            elif token in ("<", ">", "!"):
                if parent_state != JSX:
                    current_context = copy_context({
                        "type": VARIABLE_EQUALITY,
                        "left_hand": [{
                            "type": VARIABLE_OR_METHOD,
                            "variable": current_context['variable'],
                        }],
                        "equality": token
                    })
                    continue
                else:
                    tokens.insert(0, token)
                    current_context = pop_context()
                    continue
            elif token in END_STATS or ((token == "," or token == ')') and parent_state == FUNCTION_DEFINITION):
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            elif token == '.':
                current_context = copy_context({
                    "type": VARIABLE_CHAIN,
                    "items": [current_context['variable']],
                    "found_dot": True,
                })
                continue
            elif token == '(':
                current_context = copy_context({
                    "type": FUNCTION_CALL,
                    "function": [current_context],
                    "params": [],
                    "in_params": True,
                })
                continue
            elif token == "-":
                current_context = copy_context({
                    "type": VARIABLE_MANIPULATE,
                    "left_hand": [current_context],
                    "operator": token,
                })
                continue
            elif token == "[":
                current_context = copy_context({
                    "type": ARRAY_OBJECT_INDEXING,
                    "left_hand": [current_context],
                })
                continue
            elif token == ":":
                # in this case we should only get here if the variable is a part of a map
                # so we should pop context until we get to the map context
                variable = current_context['variable']
                # the first context we actually just want to remove, not pop, because this
                # context should not be added to it. I'm sure this will make something go wrong later on
                current_context = context_stack.pop()
                while len(context_stack) > 0:
                    current_context = pop_context()
                    if current_context['type'] == MAP_START:
                        break
                # push variable and colon back onto the stack so we process them as part of the map
                tokens.insert(0, variable)
                tokens.insert(0, token)
                # we need to set this so the map immediately goes to a new MAP_LINE
                current_context['last_newline'] = True
                continue
        elif current_context['type'] == VARIABLE_SET:
            if token == " ":
                continue
            elif token in END_STATS:
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            elif token == "=":
                current_context = copy_context({
                    "type": VARIABLE_EQUALITY,
                    "left_hand": current_context['left_hand'],
                    "equality": '=='
                })
                continue
            else:
                tokens.insert(0, token)
                append_context_stack()
                continue
        elif current_context['type'] == STRING_DOUBLE:
            if token == "\"":
                current_context = pop_context()
                continue
            else:
                current_context["string"] += token
                continue
        elif current_context['type'] == VARIABLE_SET:
            if token in END_STATS:
                current_context = pop_context(newline=token == "\n")
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
            elif token in END_STATS:
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            else:
                current_context = pop_context()
                continue
        elif current_context['type'] == VARIABLE_ADD_OR_INCREMENT:
            if token == "+":
                current_context = copy_context({
                    "type": VARIABLE_INCREMENT,
                    "variable": current_context['variable'],
                })
                current_context = pop_context()
                continue
            else:
                tokens.insert(0, token)
                current_context = copy_context({
                    "type": VARIABLE_MANIPULATE,
                    "left_hand": [{
                        "type": VARIABLE_OR_METHOD,
                        "variable": current_context['variable'],
                    }],
                    "operator": "+",
                })
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
            elif token in END_STATS:
                append_context_stack(True)
                continue
            else:
                # handle condition, pushing token back onto the stack
                tokens.insert(0, token)
                append_context_stack()
                continue
        elif current_context['type'] == VARIABLE_EQUALITY:
            if token == "=":
                if len(current_context['equality']) < 2:
                    current_context['equality'] += token
                    continue
            elif token in END_STATS:
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            else:
                tokens.insert(0, token)
                append_context_stack()
                continue
        elif current_context['type'] == FOR_STATEMENT:
            if token == " ":
                continue
            elif token == ";":
                if "params" not in current_context:
                    current_context['params'] = []
                current_context['params'].append(current_context['children'])
                current_context['children'] = []
                continue
            elif token == "\n":
                append_context_stack(True)
                continue
            else:
                tokens.insert(0, token)
                append_context_stack()
                continue
        elif state == FOR_AS:
            if token == " ":
                continue
            elif token == ":":
                current_context['is_object'] = True
                continue
            elif token == "\n":
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            else:
                if not current_context['is_object']:
                    current_context['as_name'] = token
                else:
                    current_context['value_name'] = token
                continue
        elif state == WHILE_STATEMENT:
            if token == " ":
                continue
            elif token == "\n":
                append_context_stack(True)
                continue
            else:
                tokens.insert(0, token)
                append_context_stack()
                continue
        elif state == CLASS_STATEMENT:
            if token == " ":
                continue
            elif token == "\n":
                append_context_stack(True)
                continue
            else:
                if current_context['class'] is None:
                    current_context['class'] = token
                else:
                    current_context['extends'] = token
                continue
        elif state == VARIABLE_CHAIN:
            if token == " ":
                continue
            elif token == ".":
                if not current_context['found_dot']:
                    current_context['found_dot'] = True
                    continue
            elif len(token) > 0 and token[0] in VALID_VARIABLE_START:
                if current_context['found_dot']:
                    current_context['items'].append(token)
                    current_context['found_dot'] = False
                    continue
            elif token == '=':
                current_context = copy_context({
                    "type": VARIABLE_SET,
                    "left_hand": [remove_spaces(current_context)],
                })
                continue
            elif token == "(":
                current_context = copy_context({
                    "type": FUNCTION_CALL,
                    "function": [current_context],
                    "params": [],
                    "in_params": True,
                })
                continue
            elif token in END_STATS:
                current_context = pop_context()
                continue
        elif state == FUNCTION_DEFINITION:
            if token == ' ':
                continue
            elif token == '(':
                if not current_context['in_params'] and len(current_context['params']) == 0:
                    current_context['in_params'] = True
                    current_context['waiting_for_param']: True
                    continue
            elif token == ",":
                if not current_context['waiting_for_param'] and current_context['in_params']:
                    current_context['waiting_for_param'] = True
                    continue
            elif token == ')':
                if not current_context['waiting_for_param'] and current_context['in_params']:
                    current_context['in_params'] = False
                    continue
                else:
                    # parent should deal with this since we're probably in a function call
                    tokens.insert(0, token)
                    current_context = pop_context()
                    continue
            elif len(token) > 0 and token[0] in VALID_VARIABLE_START:
                if current_context['in_params']:
                    current_context['params'].append(token)
                    current_context['waiting_for_param'] = False
                    continue
                else:
                    if current_context['function_name'] is None:
                        current_context['function_name'] = token
                        continue
            elif token == "\n":
                append_context_stack(True)
                continue
        elif state == FUNCTION_CALL:
            if token == '\n':
                tokens.insert(0, token)
                append_context_stack()
                continue
            elif token == ")":
                current_context = pop_context()
                continue
        elif state == END_FUNCTION_CALL:
            tokens.insert(0, token)
            current_context = pop_context()
            continue
        elif state == PRAGMA:
            if token == ' ':
                continue
            elif token == '\n':
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            elif token == ",":
                continue
            else:
                if current_context['pragma_name'] is None:
                    current_context['pragma_name'] = token
                    current_context['pragma_values'] = []
                    continue
                else:
                    current_context['pragma_values'].append(token)
                    continue
        elif state == ARRAY_START:
            if token == "\n":
                current_context['last_newline'] = True
                current_context['buffer'].append('\n')
                continue
            elif token == "\t" or token == " ":
                current_context['buffer'].append(token)
                continue
            else:
                if token == "]":
                    current_context = pop_context()
                    continue
                else:
                    if current_context['last_newline']:
                        current_context['buffer'].reverse()
                        for item in current_context['buffer']:
                            tokens.insert(0, item)
                        tokens.insert(0, token)
                        current_context['buffer'] = []
                        current_context['last_newline'] = False
                        append_context_stack()
                        continue
                    else:
                        current_context['buffer'].append(token)
                        continue
        elif state == MAP_START:
            if token == "\n":
                current_context['last_newline'] = True
                continue
            if token == " " or token == "\t":
                continue
            elif token == "}":
                current_context = pop_context()
                continue
            elif len(token) > 0 and token[0] in VALID_VARIABLE_START:
                if current_context['last_newline']:
                    current_context['last_newline'] = False
                    append_context_stack()
                    current_context = {
                        "type": MAP_LINE,
                        "key": token,
                        "spaces": 0,
                        "tabs": 0,
                        "have_colon": False,
                        "processed": False,
                        "nested": None,
                    }
                    continue
        elif state == MAP_LINE:
            if token == ":":
                if not current_context['have_colon']:
                    current_context['have_colon'] = True
                    continue
            else:
                if not current_context['processed']:
                    if current_context['have_colon']:
                        current_context['processed'] = True
                        tokens.insert(0, token)
                        append_context_stack()
                        continue
                else:
                    tokens.insert(0, token)
                    current_context = pop_context()
                    continue
        elif state == JSX:
            substate = current_context['substate']
            log("handle jsx token {}".format(substate))
            if substate == JSX_START:
                if token == "/":
                    current_context['end_tag'] = True
                    continue
                else:
                    current_context['tag'] = token
                    current_context['substate'] = JSX_ATTRIBUTES
                    continue
            elif substate == JSX_ATTRIBUTES:
                if token == ">":
                    if not current_context['end_tag'] and not current_context['self_close']:
                        # append a token so that we know we're at the end of the attributes
                        if "children" not in current_context:
                            current_context['children'] = []
                        current_context['children'].append({
                            "type": JSX_TAG_END,
                        })
                        current_context['substate'] = JSX_CHILDREN
                    else:
                        current_context = pop_context()
                        
                        if current_context['type'] == JSX:
                            # we also need to pop out of our previous jsx context since it's done
                            current_context = pop_context()
                        continue
                    continue
                elif token == "/":
                    if not current_context['end_tag']:
                        current_context['self_close'] = True
                        continue
                elif token == "\n" or token == " " or token == "\t":
                    append_context_stack()
                    current_context = copy_context({
                        "type": JSX_ATTRIBUTE,
                        "attr": None,
                        "fetching_value": False,
                        "bracket": False,
                    })
                    continue
            elif substate == JSX_CHILDREN:
                if token == ")":
                    # this is likely the end of a function call
                    current_context = pop_context()
                    continue
                else:
                    tokens.insert(0, token)
                    append_context_stack()
                    continue
            
            raise Exception("Unexpected token at line " + str(line) + ": \"" + token + "\" " + state + " -> " + substate)
        elif state == JSX_ATTRIBUTE:
            if token == "=":
                if not current_context['fetching_value']:
                    current_context['fetching_value'] = True
                    continue
            elif token == "\"":
                if current_context['fetching_value']:
                    tokens.insert(0, token)
                    current_context['fetching_value'] = False
                    append_context_stack()
                    continue
            elif token == "{":
                current_context['bracket'] = True
                append_context_stack()
                continue
            elif token == "}":
                current_context['fetching_value'] = False
                current_context = pop_context()
                continue
            elif token == " ":
                if not current_context['fetching_value']:
                    if current_context['attr'] is not None:
                        tokens.insert(0, token)
                        current_context = pop_context()
                        continue
                    else:
                        continue
            elif token == "\n":
                if not current_context['bracket']:
                    current_context = pop_context()
                    continue
                else:
                    append_context_stack()
                    continue
            elif token == "/" or token == ">":
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            elif token == "\t":
                continue
            else:
                if not current_context['fetching_value']:
                    current_context['attr'] = token
                    continue
        elif state == RETURN:
            if token == " ":
                continue
            elif token == "\n":
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            else:
                tokens.insert(0, token)
                append_context_stack()
                continue
        elif state == VARIABLE_MANIPULATE:
            if current_context['operator'] is not None:
                tokens.insert(0, token)
                append_context_stack()
                continue
        elif state == ARRAY_OBJECT_INDEXING:
            if token == "]":
                current_context = pop_context()
                continue
            else:
                tokens.insert(0, token)
                append_context_stack()
                continue
        elif state == BOOLEAN:
            tokens.insert(0, token)
            current_context = pop_context()
            continue
        elif state == ELSE_STATEMENT:
            append_context_stack(True)
            continue
        elif state == JSX_TEXT_CONTENT:
            if token == "<":
                tokens.insert(0, token)
                current_context = pop_context()
                continue
            else:
                current_context['text'] += token
                continue

        raise Exception("Unexpected token at line " + str(line) + ": \"" + token + "\" " + state)

    # pop at the very end just to make sure we handle any final contexts
    pop_all_contexts()

    return statements

def build_tree(statements):
    tree_children = []

    def unwrap_statements(children, remove_spaces = False):
        result = []
        for child in children:
            result += unwrap_statement(child, remove_spaces)

        return result

    def unwrap_statement(statement, remove_spaces = False):
        if isinstance(statement, Tree) and statement.name == 'statement':
            children = statement.children
            new_children = []
            for child in children:
                if isinstance(child, Tree) and child == Tree("spaces", [Token("SPACE", " ")]):
                    continue
                new_children.append(child)
            return new_children

        return statement

    def strip_spaces(child_arr):
        result = []
        for child in child_arr:
            if isinstance(child, Tree) and child.name == "statement":
                result.append(Tree("statement",unwrap_statement(child, True) ))
            else:
                result.append(child)
        return result

    def wrap_statement(statement, result):
        children = []
        if "spaces" in statement:
            for i in range(statement['spaces']):
                children.append(Tree("spaces", [Token("SPACE", " ")]))
        if "tabs" in statement:
            for i in range(statement['tabs']):
                children.append(Tree("spaces", [Token("TAB", "\t")]))
        children.append(result)

        return Tree("statement", children)

    def add_result(statement, result):
        tree_children.append(wrap_statement(statement, result))

    def build_nested(statement):
        nested_children = []

        if "nested_children" in statement:
            for child in statement['nested_children']:
                nested_children.append(build_tree([child])[0])

        return Tree("nested", nested_children)

    for statement in statements:
        if statement['type'] == END:
            # noop
            pass
        elif statement['type'] == VARIABLE_SET:
            child = statement['children'][0]
            child_tree = build_tree([child])[0]
            left_hand = unwrap_statements(build_tree(statement['left_hand']))

            add_result(statement, Tree("variable_assignment", left_hand + [child_tree]))
        elif statement['type'] == STRING_DOUBLE:
            add_result(statement, Tree("string", [Token("STRING_CONTENTS_DOUBLE", statement['string'])]))
        elif statement['type'] == STRING_SINGLE:
            add_result(statement, Tree("string", [Token("STRING_CONTENTS_SINGLE", statement['string'])]))
        elif statement['type'] == NEWLINE:
            tree_children.append(Token("NEWLINE", "\n"))
        elif statement['type'] == NUMBER_STATE:
            add_result(statement, Token('NUMBER', statement['number']))
        elif statement['type'] == VARIABLE_INCREMENT:
            add_result(statement, Tree('variable_increment', [
                Tree("variable", [Token('VARIABLE_NAME', statement['variable'])]),
            ]))
        elif statement['type'] == VARIABLE_COERCION:
            add_result(statement,  Tree('variable_coercion', [
                Tree("variable", [Token('VARIABLE_NAME', statement['variable'])]),
                Token('TYPE', statement['new_type']),
            ]))
        elif statement['type'] == IF_STATEMENT:
            child = statement['children'][0]
            child_tree = build_tree([child])[0]
            condition = build_tree([child])[0]
            condition_children = unwrap_statement(condition)
            condition = condition_children[0]

            nested = build_nested(statement)

            add_result(statement, Tree('if_stat', [condition, nested]))
        elif statement['type'] == VARIABLE_EQUALITY:
            left_hand_trees = build_tree(statement['left_hand'])
            children = build_tree(statement['children'])
            children = strip_spaces(children)
            result = left_hand_trees + [Token("EQUALITY", statement['equality'])] + children
            add_result(statement, Tree('condition', result))
        elif statement['type'] == VARIABLE_OR_METHOD:
            # if we got here it's clearly a variable
            add_result(statement, Tree("variable", [Token('VARIABLE_NAME', statement['variable'])]))
            continue
        elif statement['type'] == FOR_STATEMENT:
            nested = build_nested(statement)
            if "params" in statement:
                all_params = []
                for param in statement['params']:
                    all_params += build_tree(param)
                all_params += build_tree(statement['children'])

                add_result(statement, Tree('for_stat', [Tree('for_statement', all_params), nested]))
            else:
                children = build_tree(statement['children'])
                children = unwrap_statements(children)
                children.append(nested)
                add_result(statement, Tree('for_stat', children))
        elif statement['type'] == FOR_AS:
            final_children = [
                Tree('variable', [Token('VARIABLE_NAME', statement['variable'])]),
                Tree('variable', [Token('VARIABLE_NAME', statement['as_name'])]),
            ]
            if statement['is_object']:
                final_children.append(Tree('variable', [Token('VARIABLE_NAME', statement['value_name'])]))
                add_result(statement, Tree('for_object', final_children))
            else:
                add_result(statement, Tree('for_array', final_children))
        elif statement['type'] == WHILE_STATEMENT:
            children = build_tree(statement['children'])
            children = unwrap_statements(children)
            children.append(build_nested(statement))
            add_result(statement, Tree('while_stat', children))
        elif statement['type'] == CLASS_STATEMENT:
            children = [Tree("variable", [Token('VARIABLE_NAME', statement['class'])])]
            if statement['extends'] is not None:
                children.append(Tree("variable", [Token("VARIABLE_NAME", statement['extends'])]))
            children.append(build_nested(statement))
            add_result(statement, Tree('class_stat', children))
        elif statement['type'] == VARIABLE_CHAIN:
            chain = []
            for item in statement['items']:
                chain.append(Token("VARIABLE_NAME", item))
            add_result(statement, Tree("variable", [Tree("instance_variable_chain", chain)]))
        elif statement['type'] == FUNCTION_DEFINITION:
            params = []
            for param in statement['params']:
                params.append(Tree("param", [
                    Tree("variable", [Token("VARIABLE_NAME", param)]),
                ]))

            if statement['function_name'] is not None:
                params.insert(0, Tree('function_name', [
                    Tree("variable", [Token("VARIABLE_NAME", statement['function_name'])]),
                ]))
            params.append(build_nested(statement))
            add_result(statement, Tree("function_definition", params))
        elif statement['type'] == FUNCTION_CALL:
            children = [Token("NEWLINE", "\n")]
            if "children" in statement:
                for child in statement['children']:
                    results = build_tree([child])
                    children += results + [Token("NEWLINE", "\n")]

            # remove the last newline since it's extraneous
            if len(children) > 0:
                children.pop()

            children = strip_spaces(children)

            left_hand = build_tree(statement['function'])

            add_result(statement, Tree("call_function", [
                Tree("function_name", left_hand),
                Tree("function_params", children),
            ]))
        elif statement['type'] == END_FUNCTION_CALL:
            # noop
            pass
        elif statement['type'] == PRAGMA:
            children = [Token("PRAGMA_NAME", statement['pragma_name'])]
            if statement['pragma_values'] is not None:
                for value in statement['pragma_values']:
                    children.append(Token("PRAGMA_VALUE", value))
            add_result(statement, Tree("pragma", children))
        elif statement['type'] == ARRAY_START:
            children = []
            if "children" in statement:
                children = build_tree(statement['children'])
                children = strip_spaces(children)
            if "nested_children" in statement:
                nested = build_tree(statement['nested_children'])
                children += nested
            add_result(statement, Tree("array", children))
        elif statement['type'] == MAP_START:
            children = []
            if "children" in statement:
                children = build_tree(statement['children'])
            children = strip_spaces(children)
            add_result(statement, Tree("map", children))
        elif statement['type'] == MAP_LINE:
            children = build_tree(statement['children'])
            children.insert(0, Token("VARIABLE_NAME", statement['key']))
            children = strip_spaces(children)
            add_result(statement, Tree("map_row", children))
        elif statement['type'] == JSX:
            result = [Token("TAG_NAME", statement['tag'])]
            if statement['end_tag']:
                add_result(statement, Tree("jsx_end_tag", result))
            else:
                if "children" in statement:
                    children = build_tree(statement['children'])
                    result += children
                if statement['self_close']:
                    result.append(Token("TAG_SELF_CLOSE", "/"))
                add_result(statement, Tree("jsx_tag_start", result))
        elif statement['type'] == JSX_ATTRIBUTE:
            if not statement['attr']:
                continue
            children = build_tree(statement['children'])
            children.insert(0, Tree("variable", [Token("VARIABLE_NAME", statement['attr'])]))
            add_result(statement,Tree("jsx_attribute", children))
        elif statement['type'] == RETURN:
            children = build_tree(statement['children'])
            children = strip_spaces(children)
            add_result(statement, Tree("return_stmt", children))
        elif statement['type'] == VARIABLE_MANIPULATE:
            result = []
            left_hand = build_tree(statement['left_hand'])
            left_hand = strip_spaces(left_hand)
            result += left_hand

            result.append(Token("OPERATOR", statement['operator']))

            children = build_tree(statement['children'])
            children = strip_spaces(children)
            result += children

            add_result(statement, Tree("value_manipulation", result))
        elif statement['type'] == ARRAY_OBJECT_INDEXING:
            left_hand = build_tree(statement['left_hand'])
            left_hand = strip_spaces(left_hand)
            
            children = build_tree(statement['children'])
            children = strip_spaces(children)

            add_result(statement, Tree("array_object_indexing", [Tree("left_hand", left_hand), Tree("index", children)]))
        elif statement['type'] == BOOLEAN:
            add_result(statement, Tree("boolean", [
                Token(statement['boolean'].upper(), statement['boolean']),
            ]))
        elif statement['type'] == ELSE_STATEMENT:
            add_result(statement, Tree("else_stat", [build_nested(statement)]))
        elif statement['type'] == JSX_TAG_END:
            add_result(statement, Tree("jsx_tag_end", []))
        elif statement['type'] == JSX_TEXT_CONTENT:
            add_result(statement, Tree("string", [
                Token("STRING_CONTENTS_DOUBLE", statement['text']),
            ]))
        else:
            raise Exception("build_tree: Unknown type " + statement['type'])

    return tree_children