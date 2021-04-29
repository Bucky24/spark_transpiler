import ast

from lark import Transformer

TYPES = {
    "VARIABLE_ASSIGNMENT": "types/variable_assignment",
    "NEWLINE": "types/newline",
    "SPACE": "types/space",
    "STATEMENT": "types/statement",
    "IF": "types/if",
    "CALL_FUNC": "types/call_function",
    "CALL_FUNC_END": "types/call_function_end",
    "FOR_OF": "types/for_of",
    "FOR": "types/for",
    "INCREMENT": "types/increment",
    "WHILE": "types/while",
    "FUNCTION_NAME": "types/function_name",
    "FUNCTION_PARAM": "types/function_param",
    "FUNCTION": "types/function",
    "CLASS": "types/class",
    "VARIABLE_CHAIN": "types/variable_chain",
}

class SparkTransformer(Transformer):
    def _get_statement(self, tokens):
        # count the spaces
        spaces = 0
        for token in tokens:
            if token == TYPES["SPACE"]:
                spaces += 1

        return {
            "type": TYPES["STATEMENT"],
            "spaces": spaces,
            # the last entry should be the actual statement
            "statement": tokens[-1],
        }

    def STRING_CONTENTS_SINGLE(self, name):
        return "\"" + str(name) + "\""

    def STRING_CONTENTS_DOUBLE(self, name):
        return "\"" + str(name) + "\""

    def string(self, string):
        return string[0]

    def statement(self, tokens):
        return self._get_statement(tokens)

    def statement_no_space(self, tokens):
        return self._get_statement(tokens)

    def VARIABLE_NAME(self, name):
        return str(name)

    def variable(self, variable):
        return variable[0]

    def variable_assignment(self, data):
        return {
            "type": TYPES["VARIABLE_ASSIGNMENT"],
            "name": data[0],
            "value": data[1],
        }
    
    def NUMBER(self, number):
        return ast.literal_eval(number)

    def NEWLINE(self, _):
        return TYPES["NEWLINE"]

    def statements(self, statements):
        # I'm not sure if we can have multiple statements on a line right now that aren't part of another statement
        # so for now we'll just remove the newlines and continue forth

        return [
            statement
            for statement in statements
            if statement != TYPES["NEWLINE"]
        ]

    def start(self, statements):
        # actual fluff, everything is already processed
        return statements[0]

    def SPACE(self, _):
        return TYPES["SPACE"]

    def spaces(self, value):
        return value[0]

    def EQUALITY(self, value): 
        return str(value)

    def condition(self, values):
        # passthrough for now
        return values

    def if_stat(self, values):
        # right now can only have 3 children
        return {
            "type": TYPES["IF"],
            "left_hand": values[0][0],
            "condition": values[0][1],
            "right_hand": values[0][2],
        }

    def call_function(self, name):
        return {
            "type": TYPES["CALL_FUNC"],
            "function": name[0],
        }

    def end_call_function(self, _):
        return {
            "type": TYPES["CALL_FUNC_END"]
        }

    def for_array(self, values):
        return {
            "type": TYPES["FOR_OF"],
            "variable": values[0],
            "value": values[1]
        }

    def for_stat(self, children):
        return children[0]

    def for_object(self, values):
        return {
            "type": TYPES["FOR_OF"],
            "variable": values[0],
            "key": values[1],
            "value": values[2],
        }

    def for_statement(self, conditions):
        return {
            "type": TYPES["FOR"],
            "conditions": conditions,
        }

    def variable_increment(self, variable):
        return {
            "type": TYPES["INCREMENT"],
            "variable": variable[0],
        }

    def while_stat(self, condition):
        return {
            "type": TYPES["WHILE"],
            "condition": condition[0],
        }

    def function_name(self, name):
        return {
            "type": TYPES["FUNCTION_NAME"],
            "name": name[0],
        }

    def first_param(self, param):
        return {
            "type": TYPES["FUNCTION_PARAM"],
            "param": param[0],
        }

    def param(self, param):
        return {
            "type": TYPES["FUNCTION_PARAM"],
            "param": param[0],
        }

    def function_definition(self, values):
        name = None
        params = []

        for value in values:
            if value["type"] == TYPES["FUNCTION_NAME"]:
                name = value["name"]
            else:
                params.append(value["param"])

        return {
            "type": TYPES["FUNCTION"],
            "name": name,
            "params": params,
        }

    def class_stat(self, values):
        name = values[0]
        extends = values[1] if len(values) > 1 else None

        return {
            "type": TYPES["CLASS"],
            "name": name,
            "extends": extends,
        }

    def instance_variable_chain(self, variables):
        return {
            "type": TYPES["VARIABLE_CHAIN"],
            "chain": variables,
        }
            

_spark_transformer = SparkTransformer()

def process_tree(parse_tree):
    return _spark_transformer.transform(parse_tree)
