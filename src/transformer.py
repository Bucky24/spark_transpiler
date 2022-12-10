import ast

#from lark import Transformer
from grammar import Tree, Token

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
    "FUNCTION_PARAMS": "types/function_params",
    "FUNCTION": "types/function",
    "CLASS": "types/class",
    "VARIABLE_CHAIN": "types/variable_chain",
    "CONDITION": "types/condition",
    "PRAGMA": "types/pragma",
    "TAB": "types/tab",
    "ARRAY": "types/array",
    "ARRAY_END": "types/array_end",
    "MAP": "types/map_start",
    "MAP_END": "types/map_end",
    "MAP_ROW": "types/map_row",
    "JSX_END_TAG": "types/jsx_end_tag",
    "TAG_NAME": "types/tag_name",
    "JSX_END_TAG": "types/jsx_end_tag",
    "JSX_START_TAG": "types/jsx_start_tag",
    "JSX_TAG_SELF_CLOSE": "types/jsx_tag_self_close",
    "JSX_TAG_END": "types/jsx_tag_end",
    "RETURN": "types/return",
    "VALUE_MANIPULATION": "types/value_manipulation",
    "ELSE": "types/else",
    "JSX_ATTRIBUTE": "types/jsx_attribute",
    # used in preprocessor
    "BLOCK": "types/block",
    "NESTED": "types/nested",
}

# turn to true for debug logs
LOG = False

def log(str):
    if LOG:
        print(str)
    

class Transformer:
    def transform(self, tree):
        func = getattr(self, tree.name)
        if isinstance(tree, Tree):
            log("Tree " + tree.name)
            tokens = []
            for child in tree.children:
                result = self.transform(child)
                tokens.append(result)
            return func(tokens)
        elif isinstance(tree, Token):
            log("Token " + tree.name)
            return func(tree.value)

class SparkTransformer(Transformer):
    def _get_statement(self, tokens):
        # count the spaces
        spaces = 0
        for token in tokens:
            if token == TYPES["SPACE"]:
                spaces += 1
            elif token == TYPES["TAB"]:
                spaces += 4

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
        if len(string) > 0:
            return string[0]
        return "\"\""

    def statement(self, tokens):
        return self._get_statement(tokens)

    def statement_no_space(self, tokens):
        return self._get_statement(tokens)

    def statement_no_space_no_value_manip(self, tokens):
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
        
    def TAB(self, _):
        return TYPES["TAB"]

    def EQUALITY(self, value): 
        return str(value)

    def condition(self, values):
        # we expect 3 values
        return {
            "type": TYPES["CONDITION"],
            "left_hand": values[0],
            "condition": values[1],
            "right_hand": values[2],
        }

    def if_stat(self, values):
        return {
            "type": TYPES["IF"],
            "condition": values[0],
            "nested": values[1]["nested"],
        }

    def call_function(self, name):
        return {
            "type": TYPES["CALL_FUNC"],
            "function": name[0],
            "parameters": name[1] if len(name) > 1 else [],
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
        loop = children[0]
        nested = children[1]

        loop["nested"] = nested["nested"]

        return loop

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

    def while_stat(self, stats):
        return {
            "type": TYPES["WHILE"],
            "condition": stats[0],
            "nested": stats[1]["nested"],
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
        nested = []

        for value in values:
            if value["type"] == TYPES["FUNCTION_NAME"]:
                name = value["name"]
            elif value['type'] == TYPES['NESTED']:
                nested = value['nested']
            else:
                params.append(value["param"])

        return {
            "type": TYPES["FUNCTION"],
            "name": name,
            "params": params,
            "nested": nested,
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

    def PRAGMA_NAME(self, value):
        return str(value)

    def pragma(self, values):
        if len(values) == 1:
            return {
                "type": TYPES["PRAGMA"],
                "pragma": values[0],
            }
        else:
            return {
                "type": TYPES["PRAGMA"],
                "pragma": values[0],
                "value": values[1],
            }
        
    def array(self, values):
        return {
            "type": TYPES["ARRAY"],
            "children": values,
        }
        
    def map(self, values):
        return {
            "type": TYPES["MAP"],
            "children": values,
        }
        
    def map_row(self, values):
        return {
            "type": TYPES["MAP_ROW"],
            "key": values[0],
            "value": values[1],
        }
        
    def jsx_end_tag(self, values):
        return {
            "type": TYPES["JSX_END_TAG"],
            "tag": values[0],
        }

    def jsx_attribute(self, values):
        name = values[0]
        return {
            "type": TYPES['JSX_ATTRIBUTE'],
            "name": name,
            "right_hand": values[1],
        }

    def TAG_NAME(self, value):
        return {
            "type": TYPES["TAG_NAME"],
            "tag": str(value),
        }
    
    def jsx_end(self, value):
        return {
            "type": TYPES["JSX_END_TAG"],
            "tag": value[0]["tag"],
        }
        
    def jsx_tag_start(self, values):
        tag = None
        self_closes = False

        attributes = []
        children = []
        
        found_attributes = False
        for value in values:
            is_statement_with_object = value['type'] == TYPES["STATEMENT"] and isinstance(value['statement'], dict)
            if value["type"] == TYPES["TAG_NAME"]:
                tag = value["tag"]
            elif value["type"] == TYPES["JSX_TAG_SELF_CLOSE"]:
                self_closes = True
            elif is_statement_with_object and value['statement']['type'] == TYPES["JSX_TAG_END"]:
                found_attributes = True
            elif is_statement_with_object and value['statement']['type'] == TYPES["JSX_END_TAG"]:
                # at this point we're done, there should be no children left
                break
            else:
                if not found_attributes:
                    attributes.append(value)
                else:
                    children.append(value)

        return {
            "type": TYPES["JSX_START_TAG"],
            "tag": tag,
            "self_closes": self_closes,
            "attributes": attributes,
            "children": children,
        }
        
    def TAG_SELF_CLOSE(self, _):
        return {
            "type": TYPES["JSX_TAG_SELF_CLOSE"],
        }
        
    def return_stmt(self, values):
        return {
            "type": TYPES["RETURN"],
            "value": values[0],
        }

    def OPERATOR(self, value):
        return str(value)

    def value_manipulation(self, values):
        return {
            "type": TYPES["VALUE_MANIPULATION"],
            "values": values,
        }

    def else_stat(self, _):
        return {
            "type": TYPES["ELSE"],
        }
        
    def PRAGMA_VALUE(self, value):
        return str(value)

    def FALSE(self, _):
        return "false"
        
    def TRUE(self, _):
        return "true"
        
    def boolean(self, value):
        return value[0]

    def function_params(self, values):
        filtered = []
        for value in values:
            # new lines are not helpful at this point
            if value != TYPES['NEWLINE']:
                filtered.append(value)
        return {
            "type": TYPES['FUNCTION_PARAMS'],
            "params": filtered,
        }

    def jsx_tag_end(self, _):
        return {
            "type": TYPES["JSX_TAG_END"],
        }

    def nested(self, items):
        return {
            "type": TYPES["NESTED"],
            "nested": items,
        }

_spark_transformer = SparkTransformer()

def process_tree(parse_tree):
    return _spark_transformer.transform(parse_tree)
