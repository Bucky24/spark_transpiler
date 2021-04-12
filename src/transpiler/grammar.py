from lark import Lark

grammar = """
start: statements
statements: (statement NEWLINE? | NEWLINE)+

VARIABLE_NAME: ("a".."z" | "A".."Z" | "_")+
TYPE: ("a".."z" | "A".."Z" | "_")+
instance_variable_chain: VARIABLE_NAME ("." VARIABLE_NAME)+
variable: VARIABLE_NAME | instance_variable_chain
variable_assignment: variable " "* ("=" | "+=") " "* statement
variable_increment: variable " "* "++"
variable_coercion: variable " "+ "as" " "+ TYPE

STRING_CONTENTS_DOUBLE: /([^\"])+/
STRING_CONTENTS_SINGLE: /([^'])+/
string: "\\\"" STRING_CONTENTS_DOUBLE "\\\"" | "'" STRING_CONTENTS_SINGLE "'"

NUMBER: "0".."9"+ ("." "0".."9"+)?

EQUALITY: "==" | ">=" |"<=" | "<" | ">" |"!="
condition: statement " "* EQUALITY " "* statement
if: "if" " "+ condition

for_array: "for" " "+ variable " "+ "as" " "+ variable
for_object: "for" " "+ variable " "+ "as" " "+ variable " "* ":" " "* variable 
for_statement: "for" " "+ statement_no_space " "* ";" " "* statement_no_space " "* ";" " "* statement_no_space
for: for_array | for_object | for_statement

while: "while" " "+ condition

class: "class" " "+ variable (" "+ "extends" " "+ variable)?

param: "," " "* variable " "*
first_param: " "* (variable " "*)
function_name: " "+ variable
function_definition: "function" function_name? " "* "(" first_param? param* " "* ")"
call_function: variable " "* "("
end_call_function: ")"

SPACE: " "
spaces: SPACE
statement_no_space: (variable | variable_assignment | string | NUMBER | condition | if | for | variable_increment | variable_coercion | while | class | function_definition | call_function | end_call_function)
statement: spaces* (variable | variable_assignment | string | NUMBER | condition | if | for | variable_increment | variable_coercion | while | class | function_definition | call_function | end_call_function)
NEWLINE: "\\n"
"""

parser = Lark(grammar)

def parse_statement(statement):
    return parser.parse(statement)