from transformer import TYPES

_DEFAULT_SPACES = 4

_COMMON_FUNCS = [
    "print",
]

def _add_spaces(spaces):
    code = ""
    # I hate for loops in Python
    counter = 0
    while counter < spaces:
        code += " "
        counter += 1

    return code

def generate_js(transformed_tree):
    code = {
        "backend": "",
        "frontend": "",
    }
    blocks = [
        {
            "variables_generated": [],
            "spaces": 0,
            "pervious_spaces": 0,
            "is_function_call": False,
            "is_class": False,
        }
    ]
    next_statement_starts_block = False
    classes = {
        "backend": [],
        "frontend": [],
    }
    function_calls = {
        "backend": [],
        "frontend": [],
    }
    current_platform = "backend"
    def _end_block(current_block):
        # block ends
        old_block = current_block
        blocks.pop(-1)
        current_block = blocks[-1]
        code[current_platform] += _add_spaces(spaces)
        #print("ending block", old_block)
        if old_block["is_function_call"]:
            pass
        else:
            code[current_platform] += "}"
        code[current_platform] += "\n"
        return current_block
        
    # close all the blocks that need to be closed. Because blocks know how much they were indented,
    # and the closing brace is actually at the level of the PREVIOUS block, we need to loop through
    # and on each level, close the previous level.
    def _unwind_blocks():
        prev_spaces = None
        #print("next statement", next_statement_starts_block)
        if next_statement_starts_block:
            # we will get here when a block was opened but was empty,
            # and we never had anything inside it, so we need to make up
            # the block based on what type of statement we were dealing with
            prev_spaces = {
                "spaces": 0,
                "is_function_call": next_statement_starts_block == "function_call",
            }

        for block in blocks:
            if prev_spaces is not None:
                # print("here", prev_spaces)
                code[current_platform] += _add_spaces(block["spaces"])
                if prev_spaces["is_function_call"]:
                    code[current_platform] += ")\n"
                else:
                    code[current_platform] += "}\n"
            prev_spaces = block
    
    for statement in transformed_tree:
        if statement["type"] == TYPES["STATEMENT"]:
            spaces = statement["spaces"]
            
            #print('statement is', statement)

            current_block = blocks[-1]

            if next_statement_starts_block:
                old_block = current_block
                blocks.append({
                    "variables_generated": [],
                    "spaces": spaces,
                    "is_function_call": next_statement_starts_block == "function_call",
                    "previous_spaces": old_block["spaces"],
                    "is_class": next_statement_starts_block == "class",
                })
                current_block = blocks[-1]
                next_statement_starts_block = False
                
                # now we have to deal with the possibility that we're actually ending the previous block and starting a new one in the same go
                if current_block["spaces"] == old_block["spaces"]:
                    current_block = _end_block(current_block)
                    
            current_block = blocks[-1]

            # at this point we need to figure out ALL the variables that have been generated up until
            # this point, since all parent variables are in scope with child blocks
            child_variables = []
            for block in blocks:
                child_variables += block["variables_generated"]

            if current_block["spaces"] > spaces and len(blocks) > 1:
                #print("ending block 2")
                current_block = _end_block(current_block)

            result = process_statement(statement["statement"], child_variables, spaces, current_block["is_class"], classes[current_platform])
            if result:
                statement_code = result["statement"]
                
                if statement_code is None:
                    continue
                
                current_block["variables_generated"] += result.get("new_variables", [])

                code[current_platform] += _add_spaces(spaces)
                code[current_platform] += statement_code
                start_block = result.get("start_block", False)
                
                classes[current_platform] += result.get("new_classes", [])
                function_calls[current_platform] += result.get("new_function_calls", [])
                
                #print(statement_code, start_block)

                if start_block:
                    # print("starts block?", start_block)
                    next_statement_starts_block = start_block
                else:
                    if current_block["is_function_call"]:
                        # we're in the middle of calling a function so we need to separate the params by commas
                        code[current_platform] += ","
                    else:
                        code[current_platform] += ";"
                
                code[current_platform] += "\n"
            else:
                print("Error processing statement: no generator output", statement)
        else:
            raise RuntimeError("Unexpected top level statement {}".format(statement.type))
    blocks.reverse()

    # finally unwind all blocks for whatever platform we are currently on
    _unwind_blocks()

    # add in the required imports based on what has been called
    requirement_files = {
        "backend": [],
        "frontend": [],
    }
    for platform in function_calls.keys():
        required_common = []
        for function_call in function_calls[platform]:
            if function_call in _COMMON_FUNCS:
                required_common.append(function_call)

        requirements = ""

        if required_common:
            requirements += "const {\n    " + ",\n    ".join(required_common) + "\n} = require(\"./stdlib_js_common.js\");\n";
            requirement_files[platform].append({
                "type": "stdlib",
                "lang": "js",
                "library": "common",
                "extension": "js",
            })

        if requirements != "":
            code[platform] = requirements + "\n" + code[platform]

    return code, requirement_files

def process_statement(statement, variables_generated, spaces, is_class, classes):
    if isinstance(statement, str) or isinstance(statement, float) or isinstance(statement, int):
        return {
            "statement": statement,
        }

    if statement["type"] == TYPES["STATEMENT"]:
        return process_statement(statement["statement"], variables_generated, spaces, is_class, classes)
    elif statement["type"] == TYPES["VARIABLE_ASSIGNMENT"]:
        #print("processing ", statement["value"])
        value = process_statement(statement["value"], variables_generated, spaces, is_class, classes)
        str_value = value["statement"]
        start_block = value.get("start_block", None)
        if statement["name"] in variables_generated:
            return {
                "statement": "{} = {}".format(statement["name"], str_value),
                "start_block": start_block,
                "new_function_calls": value.get("new_function_calls", []), 
            }
        else:
            return {
                "statement": "var {} = {}".format(statement["name"], str_value),
                "new_variables": [statement["name"]],
                "start_block": start_block,
                "new_function_calls": value.get("new_function_calls", []), 
            }
    elif statement["type"] == TYPES["INCREMENT"]:
        return {
            "statement": "{}++".format(statement["variable"]),
        }
    elif statement["type"] == TYPES["IF"]:
        conditional = process_statement(statement["condition"], variables_generated, spaces, is_class, classes)
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
        result = process_statement(statement["conditions"][0], variables_generated, spaces, is_class, classes)
        variables += result.get("new_variables", [])
        cond1 = result["statement"]
        result = process_statement(statement["conditions"][1], variables_generated, spaces, is_class, classes)
        variables += result.get("new_variables", [])
        cond2 = result["statement"]
        result = process_statement(statement["conditions"][2], variables_generated, spaces, is_class, classes)
        variables += result.get("new_variables", [])
        cond3 = result["statement"]
        
        return {
            "statement": "for ({};{};{})".format(cond1, cond2, cond3) + " {",
            "start_block": "for",
            "new_variables": variables,
        }
    elif statement["type"] == TYPES["CONDITION"]:
        left_hand = process_statement(statement["left_hand"], variables_generated, spaces, is_class, classes)
        left_hand = left_hand["statement"]
        right_hand = process_statement(statement["right_hand"], variables_generated, spaces, is_class, classes)
        right_hand = right_hand["statement"]
        
        return {
            "statement": "{} {} {}".format(left_hand, statement["condition"], right_hand),
        }
    elif statement["type"] == TYPES["WHILE"]:
        condition = process_statement(statement["condition"], variables_generated, spaces, is_class, classes)
        return {
            "statement": "while ({})".format(condition["statement"]) + " {",
            "start_block": "while",
        }
    elif statement["type"] == TYPES["FUNCTION"]:
        name = statement.get("name", "")
        if name is None:
            name = ""
        elif not is_class:
            name = " {}".format(name)
            
        param_str = ", ".join(statement["params"])
        
        if is_class:
            return {
                "statement": "{}({})".format(name, param_str) + " {",
                "start_block": "function",
            }
        

        return {
            "statement": "function{}({})".format(name, param_str) + " {",
            "start_block": "function",
        }
    elif statement["type"] == TYPES["CALL_FUNC"]:
        name = process_statement(statement["function"], variables_generated, spaces, is_class, classes)
        name = name["statement"]
        if name in classes:
            return {
                "statement": "new {}(".format(name),
                "start_block": "function_call",
            }
        return {
            "statement": "{}(".format(name),
            "start_block": "function_call",
            "new_function_calls": [name],
        }
    elif statement["type"] == TYPES["CALL_FUNC_END"]:
        return {
            "statement": ")",
        }
    elif statement["type"] == TYPES["CLASS"]:
        extends = statement.get("extends", None)
        if not extends:
            return {
                "statement": "class {}".format(statement["name"]) + " {",
                "start_block": "class",
                "new_classes": [statement["name"]],
            }
        else:
            return {
                "statement": "class {} extends {}".format(statement["name"], extends) + " {",
                "start_block": "class",
                "new_classes": [statement["name"]],
            }
    elif statement["type"] == TYPES["VARIABLE_CHAIN"]:
        return {
            "statement": ".".join(statement["chain"]),
        }
    elif statement["type"] == TYPES["PRAGMA"]:
        return {
            "statement": None,
            "new_platform": statement["pragma"].lower(),
        }