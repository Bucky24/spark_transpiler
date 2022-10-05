import json

from transformer import TYPES
from utils import build_import_filename

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

"""
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

        new_args = args.copy()
        new_args['spaces'] += _DEFAULT_SPACES
        params = process_statement(statement['parameters'], new_args)
        if params['statement'] == '':
            code += ")"
        else:
            code += "\n" + params['statement'] + "\n)"

        return {
            "statement": "{}".format(code),
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
        if len(statement['children']) > 0:
            childs = []
            for child in statement['children']:
                child_result = process_statement(child, args)
                childs.append(_add_spaces(_DEFAULT_SPACES) + child_result['statement'])
             
            code = "{\n" + ",\n".join(childs) + "\n}"
            return {
                "statement": code,
            }
        else:
            return {
                "statement": "{}",
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

        attribute_code = "{"
        if len(statement['attributes']) > 0:
            attribute_code += "\n"
        new_args = args.copy()
        new_args['spaces'] += _DEFAULT_SPACES
        for attribute in statement['attributes']:
            processed = process_statement(attribute, new_args)
            attribute_code += processed['statement'] + "\n"

        if len(statement['attributes']) > 0:
            attribute_code += _add_spaces(args['spaces'])
        attribute_code += "}"

        new_classes = ["Component"]
        if statement["self_closes"]:
            return {
                "statement": code + attribute_code + ", [])",
                "new_class_calls": new_classes,
            }
        else:
            return {
                "statement": code + attribute_code +", [",
                "start_block": "jsx_children",
                "new_class_calls": new_classes,
            }
    elif statement["type"] == TYPES["JSX_END_TAG"]:
        return {
            "statement": "])",
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
    elif statement['type'] == TYPES['JSX_ATTRIBUTE']:
        right_hand = process_statement(statement['right_hand'], args)

        return {
            "statement": _add_spaces(args['spaces']) + statement['name'] + ": " + right_hand['statement'] + ",",
        }
    elif statement['type'] == TYPES['FUNCTION_NAME']:
        return process_statement(statement['name'], args)
    elif statement['type'] == TYPES['FUNCTION_PARAMS']:
        results = []
        for param in statement['params']:
            # where is this even coming from?
            if param == "types/newline":
                continue

            param_processed = process_statement(param, args)
            param_code = param_processed['statement']
            if param_code is not None:
                lines = param_code.split("\n")
                # we now have to add the spaces to each line in the output because this is
                # a function param. Need a better way to do this honestly :D
                fixed_lines = []
                for line in lines:
                    fixed_lines.append(_add_spaces(_DEFAULT_SPACES) + line)
                results.append("\n".join(fixed_lines))
        if len(results) == 1:
            return {
                "statement": results[0]
            }
        return {
            "statement": ",\n".join(results),
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
"""

def generate_js(tree, function_imports, class_imports, label, env):
    if len(tree) == 0:
        return {
            "code": None,
            "imports": [],
        }

    all_imported_classes = []
    for import_type in class_imports:
        all_imported_classes += class_imports[import_type]

    result = generate_code(tree, {
        "generated_variables": [],
        "generated_classes": all_imported_classes,
    })

    import_files = {}

    for import_type in function_imports:
        import_files[import_type] = {
            "env": env,
            "lang": "js",
            "library": import_type,
            "extension": "js",
        }

    for import_type in class_imports:
        import_files[import_type] = {
            "env": env,
            "lang": "js",
            "library": import_type,
            "extension": "js",
        }

    if env == "backend":
        code = result['code']

        for import_type in function_imports:
            import_values = function_imports[import_type]
            file = build_import_filename(import_files[import_type])
            import_code = "const {\n    " + ",\n    ".join(import_values) + "\n} = require(\"./" + file + "\");\n\n"
            code = import_code + code

        if len(result['exports']) > 0:
            if len(result['exports']) == 1:
                code += "\n\nmodule.exports = {\n\t" + result['exports'][0] + "\n};\n"
            else:
                code += "\n\nmodule.exports = {\n\t" + "\n\t".join(result['exports']) + "};\n"
        code = wrap_backend(code)
    elif env == "frontend":
        code = wrap_frontend(result['code'], label)

        for import_type in function_imports:
            import_values = function_imports[import_type]
            file = build_import_filename(import_files[import_type])
            import_code = "import {\n    " + ",\n    ".join(import_values) + "\n} from \"./" + file + "\";\n\n"
            code = import_code + code

        for import_type in class_imports:
            import_values = class_imports[import_type]
            file = build_import_filename(import_files[import_type])
            import_code = "import {\n    " + ",\n    ".join(import_values) + "\n} from \"./" + file + "\";\n\n"
            code = import_code + code

    return {
        "code": code,
        "imports": list(import_files.values()),
    }

def wrap_backend(code):
    return "(async () => {\n" + code + "\n})();\n"

def wrap_frontend(code, label):
    return "Modules[\"" + label + "\"] = (async () => {\nawait new Promise((resolve) => {setTimeout(resolve, 10);});\n" + code + "\n})();\n"

def generate_code(tree, context = None):
    if not isinstance(tree, list):
        tree = [tree]

    code_lines = []
    exports = []
    set_context_type = None
    new_classes = []

    if context is None:
        context = {
            "generated_variables": [],
            "generated_classes": [],
        }

    def add_code(code, additional_spaces = 0):
        spaces = context['spaces'] if 'spaces' in context else 0
        spaces += additional_spaces
        # apply spaces to all lines equally
        lines = code.split("\n")
        new_lines = []
        for line in lines:
            new_lines.append(" " * spaces + line)
        code = "\n".join(new_lines)
        code_lines.append(code)

    def remove_spaces(code):
        lines = code.split("\n")
        min_spaces = 0
        for char in lines[0]:
            if char == " ":
                min_spaces += 1
            else:
                break
        new_lines = []
        for line in lines:
            new_lines.append(line[min_spaces:])
        return "\n".join(new_lines)

    def add_export(export):
        exports.append(export)

    def add_new_class(class_name):
        new_classes.append(class_name)

    def indent_code(code, indent):
        lines = code.split("\n")
        new_lines = []
        for line in lines:
            new_lines.append(" "*indent + line)
        return "\n".join(new_lines)

    def count_spaces(code):
        spaces = 0
        for char in code:
            if char == " ":
                spaces += 1
            else:
                return spaces
        return spaces

    def passthrough_context(result):
        nonlocal set_context_type

        for export in result['exports']:
            add_export(export)
        if "context_type" in result:
            set_context_type = result['context_type']
        for class_name in result['new_classes']:
            add_new_class(class_name)

    parent_context_type = context['parent_type'] if "parent_type" in context else None

    for statement in tree:
        log("Generating for " + statement['type'])
        if statement['type'] == TYPES['STATEMENT']:
            if isinstance(statement['statement'], str) or isinstance(statement['statement'], float) or isinstance(statement['statement'], int):
                add_code(str(statement['statement']))
                continue
            new_context = context.copy()
            new_context['spaces'] = statement['spaces'] + (context['spaces'] if "spaces" in context else 0)
            result = generate_code(statement['statement'], new_context)
            add_code(result['code'])
            passthrough_context(result)
        elif statement['type'] == TYPES['VARIABLE_ASSIGNMENT']:
            value = generate_code(statement['value'], context)['code']
            value = value.lstrip()
            code = ""
            if value[-1] == ";":
                # we handle the semicolon ourselves
                value = value[:-1]
            if statement['name'] not in context['generated_variables']:
                code += "let "
                context['generated_variables'].append(statement['name'])
            code += statement['name'] + " = " + value + ";"
            add_code(code)
        elif statement['type'] == TYPES['INCREMENT']:
            add_code(statement['variable'] + "++")
        elif statement['type'] == TYPES['BLOCK']:
            opening_statement_result = generate_code(statement['statement'], context)
            opening_statement = opening_statement_result['code']
            new_context_type = opening_statement_result['context_type']
            if opening_statement[-1] == "\n":
                opening_statement = opening_statement[:-1]
            new_context = context.copy()
            new_context['parent_type'] = new_context_type
            child_code = generate_code(statement['children'], new_context)['code']
            # we can extrapolate the necessary indent for the end } by looking at the opening statement
            end_spaces = count_spaces(opening_statement)
            if child_code != "":
                add_code(opening_statement + "\n" + child_code + "\n" + " "*end_spaces + "}")
            else:
                add_code(opening_statement + "\n"  + " "*end_spaces + "}")
            passthrough_context(opening_statement_result)
        elif statement['type'] == TYPES['IF']:
            condition_code = generate_code(statement['condition'], context)['code'].lstrip()
            add_code("if (" + condition_code + ") {")
        elif statement['type'] == TYPES['CONDITION']:
            left_hand = generate_code(statement['left_hand'], context)['code'].lstrip()
            right_hand = generate_code(statement['right_hand'], context)['code'].lstrip()

            add_code(left_hand + " " + statement['condition'] + " " + right_hand)
        elif statement['type'] == TYPES['FOR_OF']:
            if "key" in statement:
                add_code("for (let " + statement['key'] + ' in ' + statement['variable'] + ") {")
                add_code(" "*4 + "let " + statement['value'] + " = " + statement['variable'] + "[" + statement['key'] + "];")
            else:
                add_code("for (let " + statement['value'] + ' of ' + statement['variable'] + ") {")
        elif statement['type'] == TYPES['FOR']:
            condition_list = []
            for condition_str in statement['conditions']:
                condition_code = generate_code(condition_str, context)['code']
                if condition_code[-1] == ";":
                    condition_code = condition_code[:-1]
                condition_list.append(condition_code)
            conditions = ";".join(condition_list)
            add_code("for (" + conditions + ") {")
        elif statement['type'] == TYPES['WHILE']:
            condition_code = generate_code(statement['condition'], context)['code']
            add_code("while (" + condition_code + ") {")
        elif statement['type'] == TYPES['FUNCTION']:
            start = "async "
            if parent_context_type != "class":
                start += "function "
            if statement['name'] == 'constructor':
                # we must handle this one specifically, its a class constructor
                # we call it "construct" because a JS constructor can't actually do async.
                # the actual constructor we create for the class will handle calling this
                add_code(start + "__construct(" + ", ".join(statement['params']) + ") {")
            elif statement['name'] is not None:
                add_code(start + statement['name'] + "(" + ", ".join(statement['params']) + ") {")
                add_export(statement['name'])
            else:
                add_code("async (" + ",".join(statement['params']) + ") => {")
        elif statement['type'] == TYPES['CALL_FUNC']:
            new_context = context.copy()
            new_context['spaces'] = 0

            parameter_code = generate_code(statement['parameters'], new_context)['code']
            func_name = generate_code(statement['function'], new_context)['code']\

            code = "await " + func_name + "("
            # have to handle class instance creation here
            if func_name in context['generated_classes']:
                code = "await " + func_name + "::__new("

            if parameter_code != "":
                code += "\n" + parameter_code + "\n"
            code += ");"
            add_code(code)
        elif statement['type'] == TYPES['FUNCTION_PARAMS']:
            param_codes = []
            for param in statement['params']:
                new_context = context.copy()
                new_context['spaces'] = 0
                param_code = generate_code(param, new_context)['code']
                if param_code[-1] == ";":
                    param_code = param_code[:-1]
                param_code = remove_spaces(param_code)
                param_code = indent_code(param_code, 4)
                param_codes.append(param_code)
            add_code(",\n".join(param_codes))
        elif statement['type'] == TYPES['FUNCTION_NAME']:
            result = generate_code(statement['name'])
            add_code(result['code'])
        elif statement['type'] == TYPES['CLASS']:
            code = "class " + statement['name']
            if statement['extends'] is not None:
                code += " extends " + statement['extends']
            code += " {"
            add_code(code)
            # now add in the method that makes the new class
            add_code("static async __new() {", 4)
            add_code("const instance = new " + statement['name'] + "();", 8)
            add_code("if (typeof instance.__construct !== 'undefined') {", 8)
            add_code("await instance.__construct.apply(instance, arguments);", 12)
            add_code("}", 8)
            add_code("return instance;", 8)
            add_code("}", 4)
            add_export(statement['name'])
            add_new_class(statement['name'])
            context['generated_classes'].append(statement['name'])
            set_context_type = "class"
        elif statement['type'] == TYPES["VARIABLE_CHAIN"]:
            add_code(".".join(statement['chain']))
        elif statement['type'] == TYPES['ARRAY']:
            all_child_codes = []
            for child in statement['children']:
                new_context = context.copy()
                new_context['spaces'] = 0
                child_code = generate_code(child, new_context)['code']
                child_code = remove_spaces(child_code)
                child_code = indent_code(child_code, 4)
                all_child_codes.append(child_code)
            final_child_code = ",\n".join(all_child_codes)
            add_code("[\n" + final_child_code + "\n]")
        elif statement['type'] == TYPES['MAP']:
            all_child_codes = []
            for child in statement['children']:
                child_code = generate_code(child, context)['code']
                child_code = indent_code(child_code.lstrip(), 4)
                all_child_codes.append(child_code)
            final_child_code = ",\n".join(all_child_codes)
            add_code("{\n" + final_child_code + "\n}")
        elif statement['type'] == TYPES["MAP_ROW"]:
            value_code = generate_code(statement['value'], context)['code']
            add_code("\"" + statement['key'] + "\": " + value_code.lstrip())
        elif statement['type'] == TYPES["JSX_START_TAG"]:
            print(statement)
        else:
            raise Exception("Generation: don't know how to handle " + statement['type'])
    if len(code_lines) == 1:
        return {
            "code": code_lines[0],
            "exports": exports,
            "context_type": set_context_type,
            "new_classes": new_classes,
        }

    return {
        "code": "\n".join(code_lines),
        "exports": exports,
        "context_type": set_context_type,
        "new_classes": new_classes,
    }