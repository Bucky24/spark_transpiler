
from transformer import TYPES

def generate_js(transformed_tree):
    code = ""
    variables_generated = []
    for statement in transformed_tree:
        if statement["type"] == TYPES["STATEMENT"]:
            spaces = statement["spaces"]
            
            print(statement)

            result = process_statement(statement["statement"], variables_generated)
            statement = result["statement"]
            variables_generated += result.get("new_variables", [])
            code += statement + ";\n"
        else:
            raise RuntimeError("Unexpected top level statement {}".format(statement.type))
    return code

def process_statement(statement, variables_generated):
    if isinstance(statement, str) or isinstance(statement, float) or isinstance(statement, int):
        return {
            "statement": statement,
        }

    if statement["type"] == TYPES["STATEMENT"]:
        return process_statement(statement["statement"], variables_generated)
    elif statement["type"] == TYPES["VARIABLE_ASSIGNMENT"]:
        value = process_statement(statement["value"], variables_generated)
        value = value["statement"]
        if statement["name"] in variables_generated:
            return {
                "statement": "{} = {}".format(statement["name"], value),
            }
        else:
            return {
                "statement": "var {} = {}".format(statement["name"], value),
                "new_variables": [statement["name"]],
            }
    elif statement["type"] == TYPES["INCREMENT"]:
        return {
            "statement": "{}++".format(statement["variable"]),
        }
