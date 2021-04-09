from lark import Lark

grammar = """
start: statements
statements: (statement NEWLINE? | NEWLINE)+

VARIABLE_NAME: ("a".."z" | "A".."Z" | "_")+
TYPE: ("a".."z" | "A".."Z" | "_")+
variable_assignment: VARIABLE_NAME " "* ("=" | "+=") " "* statement
variable_increment: VARIABLE_NAME " "* "++"
variable_coercion: VARIABLE_NAME " "+ "as" " "+ TYPE

STRING_CONTENTS_DOUBLE: /([^\"])+/
STRING_CONTENTS_SINGLE: /([^'])+/
string: "\\\"" STRING_CONTENTS_DOUBLE "\\\"" | "'" STRING_CONTENTS_SINGLE "'"

NUMBER: "0".."9"+ ("." "0".."9"+)?

EQUALITY: "==" | ">=" |"<=" | "<" | ">" |"!="
condition: statement " "* EQUALITY " "* statement
if: "if" " "+ condition

for_array: "for" " "+ VARIABLE_NAME " "+ "as" " "+ VARIABLE_NAME
for_object: "for" " "+ VARIABLE_NAME " "+ "as" " "+ VARIABLE_NAME " "* ":" " "* VARIABLE_NAME 
for_statement: "for" " "+ statement " "* ";" " "* statement " "* ";" " "* statement
for: for_array | for_object | for_statement

SPACE: " "
statement: SPACE* (VARIABLE_NAME | variable_assignment | string | NUMBER | condition | if | for | variable_increment | variable_coercion)
NEWLINE: "\\n"
"""

parser = Lark(grammar)

def parse_statement(statement):
    return parser.parse(statement)