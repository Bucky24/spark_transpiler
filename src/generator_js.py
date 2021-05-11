from transformer import TYPES

_DEFAULT_SPACES = 4

def _add_spaces(spaces):
    code = ""
    # I hate for loops in Python
    counter = 0
    while counter < spaces:
        code += " "
        counter += 1

    return code

def generate_js(transformed_tree):
    code = ""
    blocks = [
        {
            "variables_generated": [],
            "spaces": 0,
            "is_function_call": False,
        }
    ]
    next_statement_starts_block = False
    for statement in transformed_tree:
        if statement["type"] == TYPES["STATEMENT"]:
            spaces = statement["spaces"]

            if next_statement_starts_block:
                blocks.append({
                    "variables_generated": [],
                    "spaces": spaces,
                    "is_function_call": next_statement_starts_block == "function_call",
                })
                next_statement_starts_block = False
            
            #print(statement)
            current_block = blocks[-1]

            # at this point we need to figure out ALL the variables that have been generated up until
            # this point, since all parent variables are in scope with child blocks
            child_variables = []
            for block in blocks:
                child_variables += block["variables_generated"]

            if current_block["spaces"] > spaces and len(blocks) > 1:
                # block ends
                old_block = current_block
                blocks.pop(-1)
                current_block = blocks[-1]
                code += _add_spaces(spaces)
                if old_block["is_function_call"]:
                    code += ")"
                else:
                    code += "}"
                    
                if current_block["is_function_call"]:
                    # this situation can happen with nested function calls
                    code += ","
                    
                code += "\n"

            result = process_statement(statement["statement"], child_variables, spaces)
            if result:
                statement_code = result["statement"]
                
                if statement_code is None:
                    continue
                
                current_block["variables_generated"] += result.get("new_variables", [])

                code += _add_spaces(spaces)
                code += statement_code
                start_block = result.get("start_block", False)
                
                #print(statement_code, start_block)

                if start_block:
                    next_statement_starts_block = start_block
                else:
                    if block["is_function_call"]:
                        # we're in the middle of calling a function so we need to separate the params by commas
                        code += ","
                    else:
                        code += ";"
                
                code += "\n"
            else:
                print("Error processing statement: no generator output", statement)
        else:
            raise RuntimeError("Unexpected top level statement {}".format(statement.type))
    blocks.reverse()
    # close all the blocks that need to be closed. Because blocks know how much they were indented,
    # and the closing brace is actually at the level of the PREVIOUS block, we need to loop through
    # and on each level, close the previous level.
    
    prev_spaces = -1
    if next_statement_starts_block:
        # we will get here when a block was opened but was empty,
        # and we never had anything inside it
        # in this case just set prev_spaces to SOMETHING, since we
        # don't actually use the value other than a flag it doesn't
        # matter what
        prev_spaces = 0
    
    for block in blocks:
        if prev_spaces != -1:
            code += _add_spaces(block["spaces"]) + "}\n"
        prev_spaces = block["spaces"]


    return code

def process_statement(statement, variables_generated, spaces):
    if isinstance(statement, str) or isinstance(statement, float) or isinstance(statement, int):
        return {
            "statement": statement,
        }

    if statement["type"] == TYPES["STATEMENT"]:
        return process_statement(statement["statement"], variables_generated, spaces)
    elif statement["type"] == TYPES["VARIABLE_ASSIGNMENT"]:
        value = process_statement(statement["value"], variables_generated, spaces)
        str_value = value["statement"]
        start_block = value.get("start_block", None)
        if statement["name"] in variables_generated:
            return {
                "statement": "{} = {}".format(statement["name"], str_value),
                "start_block": start_block,
            }
        else:
            return {
                "statement": "var {} = {}".format(statement["name"], str_value),
                "new_variables": [statement["name"]],
                "start_block": start_block,
            }
    elif statement["type"] == TYPES["INCREMENT"]:
        return {
            "statement": "{}++".format(statement["variable"]),
        }
    elif statement["type"] == TYPES["IF"]:
        conditional = process_statement(statement["condition"], variables_generated, spaces)
        conditional = conditional["statement"]

        return {
            "statement": "if ({})".format(conditional) + " {",
            "start_block": "if"
        }
    elif statement["type"] == TYPES["FOR_OF"]:
        key = statement.get("key", None)
        
        if key is not None:
            return {
                "statement": "for (var {} in {})".format(statement["key"], statement["variable"]) + " {\n" + _add_spaces(_DEFAULT_SPACES) + "var {} = {}[{}];".format(statement["value"], statement["variable"], statement["key"]),
                "start_block": True,
            }

        return {
            "statement": "for (var {} of {})".format(statement["value"], statement["variable"]) + " {",
            "start_block": "for",
        }
    elif statement["type"] == TYPES["FOR"]:
        variables = []
        # we expect 3 conditions, no more, no less
        result = process_statement(statement["conditions"][0], variables_generated, spaces)
        variables += result.get("new_variables", [])
        cond1 = result["statement"]
        result = process_statement(statement["conditions"][1], variables_generated, spaces)
        variables += result.get("new_variables", [])
        cond2 = result["statement"]
        result = process_statement(statement["conditions"][2], variables_generated, spaces)
        variables += result.get("new_variables", [])
        cond3 = result["statement"]
        
        return {
            "statement": "for ({};{};{})".format(cond1, cond2, cond3) + " {",
            "start_block": "for",
            "new_variables": variables,
        }
    elif statement["type"] == TYPES["CONDITION"]:
        left_hand = process_statement(statement["left_hand"], variables_generated, spaces)
        left_hand = left_hand["statement"]
        right_hand = process_statement(statement["right_hand"], variables_generated, spaces)
        right_hand = right_hand["statement"]
        
        return {
            "statement": "{} {} {}".format(left_hand, statement["condition"], right_hand),
        }
    elif statement["type"] == TYPES["WHILE"]:
        condition = process_statement(statement["condition"], variables_generated, spaces)
        return {
            "statement": "while ({})".format(condition["statement"]) + " {",
            "start_block": "while",
        }
    elif statement["type"] == TYPES["FUNCTION"]:
        name = statement.get("name", "")
        if name is None:
            name = ""
        else:
            name = " {}".format(name)
            
        param_str = ", ".join(statement["params"])

        return {
            "statement": "function{}({})".format(name, param_str) + " {",
            "start_block": "function",
        }
    elif statement["type"] == TYPES["CALL_FUNC"]:
        return {
            "statement": "{}(".format(statement["function"]),
            "start_block": "function_call",
        }
    elif statement["type"] == TYPES["CALL_FUNC_END"]:
        return {
            "statement": None,
        }