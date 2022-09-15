import json

from transformer import TYPES

_DEFAULT_SPACES = 4

_COMMON_FUNCS = [
    "print",
]

_COMMON_CLASSES = [
    "Api",
]

_FRONTEND_CLASSES = [
    "Component",
    "Style",
    "Variable",
]

_FRONTEND_FUNCS = [
    "render",
]

_BACKEND_CLASSES = [
    "Table",
]

_BACKEND_FUNCS = [

]
_PLATFORMS = [
    "backend",
    "frontend",
]

# turn to true for debug logs
LOG = True

def log(str):
    if LOG:
        print(str)

def _add_spaces(spaces):
    code = ""
    # I hate for loops in Python
    counter = 0
    while counter < spaces:
        code += " "
        counter += 1

    return code

def generate_js(transformed_tree, label, import_data):
    code = {
        "backend": "",
        "frontend": "",
    }
    blocks = [
        {
            "variables_generated": [],
            "spaces": 0,
            "previous_spaces": 0,
            "is_function_call": False,
            "is_class": False,
            "is_array": False,
            "is_map": False,
            "is_jsx": False,
            "is_constructor": False,
        }
    ]
    import_data = import_data if import_data else { "backend": {}, "frontend": {}}
    next_statement_starts_block = False
    import_classes = {
        "backend": import_data.get("backend", {}).get("classes", []),
        "frontend": import_data.get("frontend", {}).get("classes", []),
    }
    classes = {
        "backend": [],
        "frontend": [],
    }
    function_calls = {
        "backend": [],
        "frontend": [],
    }
    class_calls = {
        "backend": [],
        "frontend": [],
    }
    pragmas = {
        "backend": [],
        "frontend": [],
    }
    new_functions = {
        "backend": [],
        "frontend": [],
    }
    required_external_modules = []
    exernal_module_list = []
    current_platform = "backend"
    def _end_block(current_block):
        # block ends
        old_block = current_block
        blocks.pop(-1)
        current_block = blocks[-1]
        code[current_platform] += _add_spaces(current_block["spaces"])
        #print("ending block", old_block)
        added_bracket = False
        if old_block["is_function_call"] or old_block["is_array"] or old_block["is_map"] or old_block["is_jsx"]:
            pass
        else:
            added_bracket = True
            code[current_platform] += "}"

        # now check the new current block, if it's jsx or a map or an array, we need a comma as well
        if added_bracket and (current_block["is_array"] or current_block["is_map"] or current_block["is_jsx"]):
            code[current_platform] += ","

        code[current_platform] += "\n"
        return current_block
        
    # close all the blocks that need to be closed. Because blocks know how much they were indented,
    # and the closing brace is actually at the level of the PREVIOUS block, we need to loop through
    # and on each level, close the previous level.
    def _unwind_blocks():
        #print("unwinding blocks")
        blocks.reverse()
        prev_spaces = None
        #print("next statement", next_statement_starts_block)
        if next_statement_starts_block:
            # we will get here when a block was opened but was empty,
            # and we never had anything inside it, so we need to make up
            # the block based on what type of statement we were dealing with
            prev_spaces = {
                "spaces": 0,
                "is_function_call": next_statement_starts_block == "function_call",
                "is_array": next_statement_starts_block == "array",
                "is_map": next_statement_starts_block == "map",
                "is_jsx": next_statement_starts_block == "jsx_children" or next_statement_starts_block == "jsx_attributes",
                "is_constructor": next_statement_starts_block == "is_constructor",
            }

        for block in blocks:
            if prev_spaces is not None:
                code[current_platform] += _add_spaces(block["spaces"])
                if prev_spaces["is_function_call"]:
                    code[current_platform] += ")\n"
                else:
                    code[current_platform] += "}\n"
            prev_spaces = block

        # pop all but the last block to reset the stack
        blocks.reverse()
        while len(blocks) > 1:
            blocks.pop()
    
    for statement in transformed_tree:
        if statement["type"] == TYPES["STATEMENT"]:
            spaces = statement["spaces"]
            
            #print('statement is', statement)
            #print(current_platform)
            #print(code[current_platform])

            current_block = blocks[-1]

            if next_statement_starts_block:
                old_block = current_block
                blocks.append({
                    "variables_generated": [],
                    "spaces": spaces,
                    "is_function_call": next_statement_starts_block == "function_call",
                    "previous_spaces": old_block["spaces"],
                    "is_class": next_statement_starts_block == "class",
                    "is_array": next_statement_starts_block == "array",
                    "is_map": next_statement_starts_block == "map",
                    "is_jsx": next_statement_starts_block == "jsx_children" or next_statement_starts_block == "jsx_attributes",
                    "is_constructor": next_statement_starts_block == "constructor",
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

            while current_block["spaces"] > spaces and len(blocks) > 1:
                #print("ending block 2")
                current_block = _end_block(current_block)
                
            all_classes = _FRONTEND_CLASSES + classes[current_platform] + _BACKEND_CLASSES + _COMMON_CLASSES + import_classes[current_platform]
 
            args = {
                "child_variables": child_variables,
                "spaces": spaces,
                "is_class": current_block["is_class"],
                "all_classes": all_classes,
                "is_jsx": current_block["is_jsx"],
                "current_platform": current_platform,
                "is_constructor":  current_block["is_constructor"],
            }

            result = process_statement(statement["statement"], args)
            if result:
                statement_code = result["statement"]

                if result.get("new_platform", None):
                    # first close all blocks
                    _unwind_blocks()
                    current_platform = result.get("new_platform")
                    
                pragmas[current_platform] += result.get("new_pragmas", [])
                
                if statement_code is None:
                    continue
                
                current_block["variables_generated"] += result.get("new_variables", [])

                code[current_platform] += _add_spaces(spaces)
                code[current_platform] += str(statement_code)
                start_block = result.get("start_block", False)
                
                classes[current_platform] += result.get("new_classes", [])
                function_calls[current_platform] += result.get("new_function_calls", [])
                class_calls[current_platform] += result.get("new_class_calls", [])
                
                # do a very simple check for if we need to include mysql module
                if (
                    isinstance(statement_code, str) and
                    "Table.SOURCE_MYSQL" in statement_code and
                    "mysql" not in exernal_module_list
                ):
                    exernal_module_list.append("mysql")
                    required_external_modules.append({
                        "module": "mysql",
                        "version": "2.18.1",
                    })

                # we only care about exporting these if it's top level
                if spaces == 0:
                    new_functions[current_platform] += result.get("new_functions", [])

                # print("current block woo!", current_block)
                if start_block:
                    # print("starts block?", start_block)
                    next_statement_starts_block = start_block
                else:
                    if current_block["is_function_call"] or current_block["is_array"] or current_block["is_map"] or current_block["is_jsx"]:
                        # we're in the middle of something that takes multiple params so we need to separate the params by commas
                        code[current_platform] += ","
                    else:
                        code[current_platform] += ";"
                
                code[current_platform] += "\n"
            else:
                print("Error processing statement: no generator output", statement)
        else:
            raise RuntimeError("Unexpected top level statement {}".format(statement.type))

    # finally unwind all blocks for whatever platform we are currently on
    _unwind_blocks()

    # add in the required imports based on what has been called
    requirement_files = {
        "backend": [],
        "frontend": [],
    }
    for platform in function_calls.keys():
        required_common = []
        required_frontend = []
        required_backend = []
        # figure out what libraries we need to load based on what we called
        for function_call in function_calls[platform]:
            if function_call in _COMMON_FUNCS:
                required_common.append(function_call)
            elif function_call in _FRONTEND_FUNCS:
                required_frontend.append(function_call)
            elif function_call in _BACKEND_FUNCS:
                required_backend.append(function_call)

        for class_call in class_calls[platform]:
            if class_call in _COMMON_CLASSES:
                required_common.append(class_call)
            if class_call in _FRONTEND_CLASSES:
                required_frontend.append(class_call)
            if class_call in _BACKEND_CLASSES:
                required_backend.append(class_call)

        requirements = ""
        exports = ""

        if required_common:
            requirements += "const {\n    " + ",\n    ".join(set(required_common)) + "\n} = require(\"./stdlib_js_" + platform + "_common.js\");\n";
            requirement_files[platform].append({
                "type": "stdlib",
                "lang": "js",
                "library": "common",
                "extension": "js",
                "category": platform,
            })
            
        if required_frontend:
            requirements += "const {\n    " + ",\n    ".join(set(required_frontend)) + "\n} = require(\"./stdlib_js_" + platform + "_frontend.js\");\n";
            requirement_files[platform].append({
                "type": "stdlib",
                "lang": "js",
                "library": "frontend",
                "extension": "js",
                "category": platform,
            })

        if required_backend:
            requirements += "const {\n    " + ",\n    ".join(set(required_backend)) + "\n} = require(\"./stdlib_js_" + platform + "_backend.js\");\n";
            requirement_files[platform].append({
                "type": "stdlib",
                "lang": "js",
                "library": "backend",
                "extension": "js",
                "category": platform,
            })

        # handle exports from this particular file
        export_list = []
        export_list += new_functions[platform]
        export_list += classes[platform]
        if export_list and platform == "backend":
            function_code = ",\n\t".join(export_list)
            exports = "\nmodule.exports = {\n\t" + function_code + "\n};\n"
            code[platform] += exports

        if export_list and platform == "frontend":
            function_code = ",\n\t".join(export_list)
            exports = "\nreturn {\n\t" + function_code + "\n};\n"
            code[platform] += exports

        # we only need to handle backend library imports here. Frontend libraries export their contents to global scope.
        if requirements != "" and platform == "backend":
            code[platform] = requirements + "\n" + code[platform]

    if code["frontend"]:
        # wrap it in an async self-calling method and export the result. Also include a small wait in front of it so we can be sure that we don't try
        # to run this code until other code is also loaded
        code["frontend"] = "Modules[\"" + (label or "label") + "\"] = (async () => {\nawait new Promise((resolve) => {setTimeout(resolve, 10);});\n//<IMPORTS>\n" + code["frontend"] + "\n})();\n";
    if code["backend"]:
        code["backend"] = "(async () => {\n" + code["backend"] + "\n})();\n"

    return {
        "code": code,
        "internal_imports": requirement_files,
        "pragmas": pragmas,
        "classes": classes,
        "external_imports": required_external_modules,
    }

def process_statement(statement, args):
    variables_generated = args["child_variables"]
    spaces = args["spaces"]
    is_class = args["is_class"]
    classes = args["all_classes"]
    is_jsx = args["is_jsx"]
    platform = args["current_platform"]
    is_constructor = args["is_constructor"]

    if isinstance(statement, str) or isinstance(statement, float) or isinstance(statement, int):
        return {
            "statement": statement,
        }


    log("Processing for " + statement['type'])
    print(statement)

    if statement["type"] == TYPES["STATEMENT"]:
        return process_statement(statement["statement"], args)
    elif statement["type"] == TYPES["VARIABLE_ASSIGNMENT"]:
        #print("processing ", statement["value"])
        value = process_statement(statement["value"], args)
        # if we got nothing good from our recursive process, just give up on this line
        if value is None:
            return None

        name = process_statement(statement["name"], args)
        if name is None:
            return None
        name = name["statement"]
        is_chain = "." in name

        str_value = value["statement"]
        start_block = value.get("start_block", None)
        if is_jsx:
            # in this case we need to treat this like an attribute
            return {
                "statement": "{}: {}".format(name, str_value),
                "start_block": start_block,
                "new_function_calls": value.get("new_function_calls", []), 
                "new_class_calls": value.get("new_class_calls", []), 
            }
        elif name in variables_generated or is_chain:
            return {
                "statement": "{} = {}".format(name, str_value),
                "start_block": start_block,
                "new_function_calls": value.get("new_function_calls", []), 
                "new_class_calls": value.get("new_class_calls", []), 
            }
        else:
            return {
                "statement": "var {} = {}".format(name, str_value),
                "new_variables": [name],
                "start_block": start_block,
                "new_function_calls": value.get("new_function_calls", []), 
                "new_class_calls": value.get("new_class_calls", []), 
            }
    elif statement["type"] == TYPES["INCREMENT"]:
        return {
            "statement": "{}++".format(statement["variable"]),
        }
    elif statement["type"] == TYPES["IF"]:
        conditional = process_statement(statement["condition"], args)
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
        result = process_statement(statement["conditions"][0], args)
        variables += result.get("new_variables", [])
        cond1 = result["statement"]
        result = process_statement(statement["conditions"][1], args)
        variables += result.get("new_variables", [])
        cond2 = result["statement"]
        result = process_statement(statement["conditions"][2], args)
        variables += result.get("new_variables", [])
        cond3 = result["statement"]
        
        return {
            "statement": "for ({};{};{})".format(cond1, cond2, cond3) + " {",
            "start_block": "for",
            "new_variables": variables,
        }
    elif statement["type"] == TYPES["CONDITION"]:
        left_hand = process_statement(statement["left_hand"], args)
        left_hand = left_hand["statement"]
        right_hand = process_statement(statement["right_hand"], args)
        right_hand = right_hand["statement"]
        
        return {
            "statement": "{} {} {}".format(left_hand, statement["condition"], right_hand),
        }
    elif statement["type"] == TYPES["WHILE"]:
        condition = process_statement(statement["condition"], args)
        return {
            "statement": "while ({})".format(condition["statement"]) + " {",
            "start_block": "while",
        }
    elif statement["type"] == TYPES["FUNCTION"]:
        name = statement.get("name", "")
        orig_name = name
        if name is None:
            name = ""
        elif not is_class:
            name = " {}".format(name)
            
        param_str = ", ".join(statement["params"])

        statement = "function{}({})".format(name, param_str) + " {"
        if name == "":
            statement = "({}) =>".format(param_str) + " {"

        if is_class:
            statement = "{}({})".format(name, param_str) + " {"

        start_block = "function"
        if name == "constructor":
            start_block = "constructor"

        if name != "constructor":
            statement = "async {}".format(statement)

        new_functions = []
        if orig_name is not None and not is_class:
            new_functions.append(orig_name)
        
        return {
            "statement": statement,
            "start_block": start_block,
            "new_functions": new_functions,
        }
    elif statement["type"] == TYPES["CALL_FUNC"]:
        name = process_statement(statement["function"], args)
        name = name["statement"]
        start_block = "function_call"
        code = "{}(".format(name)

        name_path = name.split(".")
        first_name = name_path[0]
        new_function_calls = [name]
        new_class_calls = []

        new_instance = False

        if first_name in classes:
            new_class_calls = [first_name]
            new_function_calls = []
            if len(name_path) == 1:
                new_instance = True

        if not new_instance:
            if not is_constructor:
                code = "await {}".format(code)
        else:
            code = "new {}".format(code)

        return {
            "statement": "{}".format(code),
            "start_block": start_block,
            "new_class_calls": new_class_calls,
            "new_function_calls": new_function_calls,
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
        pragma = statement["pragma"].lower()
        value = statement.get("value", "")
        
        if pragma in _PLATFORMS:
            return {
                "statement": None,
                "new_platform": pragma,
            }
        else:
            if value == "":
                return {
                    "statement": None,
                    "new_pragmas": [{
                        "type": pragma,
                    }]
                }
            else:
                return {
                    "statement": None,
                    "new_pragmas": [{
                        "type": pragma,
                        "value": value,
                    }]
                }
    elif statement["type"] == TYPES["ARRAY"]:
        return {
            "statement": "[",
            "start_block": "array",
        }
    elif statement["type"] == TYPES["ARRAY_END"]:
        return {
            "statement": "]",
        }
    elif statement["type"] == TYPES["MAP"]:
        if statement["self_closes"]:
            return {
                "statement": "{}",
            }
        else:
            return {
                "statement": "{",
                "start_block": "map",
            }
    elif statement["type"] == TYPES["MAP_END"]:
        return {
            "statement": "}",
        }
    elif statement["type"] == TYPES["MAP_ROW"]:
        value = process_statement(statement["value"], args)
        
        return {
            "statement": "\"{}\": {}".format(statement["key"], value["statement"]),
            "start_block": value.get("start_block", None),
            "new_function_calls": value.get("new_function_calls", []), 
            "new_class_calls": value.get("new_class_calls", []),
        }
    elif statement["type"] == TYPES["JSX_START_TAG"]:
        code = "new Component(\"{}\", ".format(statement["tag"])
        if statement["tag"] in classes:
            code = "new {}(".format(statement["tag"])

        new_classes = ["Component"]
        if statement["self_closes"]:
            return {
                "statement": code + "{}, [])",
                "new_class_calls": new_classes,
            }
        elif statement["tag_ends"]:
            return {
                "statement": code + "{}, [",
                "start_block": "jsx_children",
                "new_class_calls": new_classes,
            }
        else:
            return {
                "statement": code + "{",
                "start_block": "jsx_attributes",
                "new_class_calls": new_classes,
            }
    elif statement["type"] == TYPES["JSX_END_TAG"]:
        return {
            "statement": "])",
        }
    elif statement["type"] == TYPES["JSX_TAG_END"]:
        if statement["self_closes"]:
            return {
                "statement": "}, [])",
            }
        else:
            return {
                "statement": "}, [",
                "start_block": "jsx_children",
            }
    elif statement["type"] == TYPES["RETURN"]:
        value = process_statement(statement["value"], args)
        return {
            "statement": "return {}".format(value["statement"]),
            "start_block": value.get("start_block", None),
            "new_function_calls": value.get("new_function_calls", []), 
            "new_class_calls": value.get("new_class_calls", []),
        }
    elif statement["type"] == TYPES["VALUE_MANIPULATION"]:
        code = ""
        start_block = None
        new_function_calls = []
        new_class_calls = []
        for i in range(len(statement["values"])):
            is_operator = i % 2 == 1
            if is_operator:
                code += " {} ".format(statement["values"][i])
            else:
                value = process_statement(statement["values"][i], args)
                print("value!!")
                print(statement['values'][i])
                print(value)
                start_block = value.get("start_block", None)
                new_function_calls += value.get("new_function_calls", [])
                new_class_calls += value.get("new_class_calls", [])

                code += "{}".format(value["statement"])

        return {
            "statement": code,
            "start_block": start_block,
            "new_function_calls": new_function_calls,
            "new_class_calls": new_class_calls,
        }
    elif statement["type"] == TYPES["ELSE"]:
        return {
            "statement": "else {",
            "start_block": "if",
        }
    else:
        raise Exception("Can't generate for type " + statement['type'])

def generate_external_exports(exports):
    package_json = {
        "dependencies": {},
    }

    for export in exports:
        module = export['module']
        version = export['version']

        package_json['dependencies'][module] = version

    return json.dumps(package_json, indent=4), "package.json", "npm install"
