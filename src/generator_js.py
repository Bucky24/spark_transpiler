import json
import traceback

from transformer import TYPES
from utils import build_import_filename

# turn to true for debug logs
LOG = False

def log(str):
    if LOG:
        print(str)

def generate_js(tree, function_imports, class_imports, custom_imports, label, env):
    if len(tree) == 0:
        return {
            "code": None,
            "imports": [],
            "classes": [],
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
            "type": "external",
            "env": env,
            "lang": "js",
            "library": import_type,
            "extension": "js",
        }

    for import_type in class_imports:
        import_files[import_type] = {
            "type": "external",
            "env": env,
            "lang": "js",
            "library": import_type,
            "extension": "js",
        }

    for import_type in custom_imports:
        import_files[import_type] = {
            "type": "internal",
            "path": import_type + ".spark",
            "link": ("FE" if env == "frontend" else "BE") + "_" + import_type,
        }

    if env == "backend":
        code = result['code']

        for import_type in function_imports:
            import_values = function_imports[import_type]
            file = build_import_filename(import_files[import_type])
            import_code = "    const {\n        " + ",\n        ".join(import_values) + "\n    } = require(\"./" + file + "\");\n\n"
            code = import_code + code

        for import_type in class_imports:
            import_values = class_imports[import_type]
            file = build_import_filename(import_files[import_type])
            import_code = "    const {\n        " + ",\n        ".join(import_values) + "\n    } = require(\"./" + file + "\");\n\n"
            code = import_code + code

        for import_type in custom_imports:
            import_values = custom_imports[import_type]
            if len(import_values) == 1 and import_values[0] == "*":
                import_code = "    const " + import_type + " = require(\"<<<BE_" + import_type + ">>>\");\n\n"
            else:
                import_code = "    const {\n        " + ",\n        ".join(import_values) + "\n    } = require(\"<<<BE_" + import_type + ">>>\");\n\n"
            code = import_code + code

        if len(result['exports']) > 0:
            if len(result['exports']) == 1:
                code += "\n\n    module.exports = {\n        " + result['exports'][0] + "\n    };\n"
            else:
                code += "\n\n    module.exports = {\n        " + ",\n        ".join(result['exports']) + "\n    };\n"
        code = wrap_backend(code)
    elif env == "frontend":
        code = result['code']
        # statement added 4 spaces to all lines. We should remove it here
        code = remove_spaces(code)

        for import_type in custom_imports:
            import_values = custom_imports[import_type]
            if len(import_values) == 1 and import_values[0] == "*":
                import_code = "const " + import_type + " = await getModule(\"" + import_type + "\");\n\n"
            else:
                import_code = "const {\n    " + ",\n    ".join(import_values) + "\n} = await getModule(\"" + import_type + "\");\n\n"
            code = import_code + code

        if len(result['exports']) > 0:
            code += "\n\nreturn {\n"
            if len(result['exports']) == 1:
                code += "    " + result['exports'][0] + "\n};\n"
            else:
                code += "    " + ",\n    ".join(result['exports']) + "\n};\n"
        code = wrap_frontend(code, label)

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
        "classes": result['new_classes'],
    }

def wrap_backend(code):
    return "(async () => {\n" + code + "\n})();\n"

def wrap_frontend(code, label):
    # at this point we're loading modules which can await at top level
    return code

def remove_spaces(code):
    lines = code.split("\n")
    min_spaces = count_spaces(lines[0])
    new_lines = []
    for line in lines:
        new_lines.append(line[min_spaces:])
    return "\n".join(new_lines)

def count_spaces(code):
    spaces = 0
    for char in code:
        if char == " ":
            spaces += 1
        else:
            return spaces
    return spaces

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

    parent_context_type = context['parent_type'] if "parent_type" in context else None

    def add_code(code, additional_spaces = 0, do_add_spaces = True):
        if do_add_spaces:
            code = add_spaces(code, additional_spaces)
        code_lines.append(code)

    def add_spaces(code, spaces):
        lines = code.split("\n")
        new_lines = []
        for line in lines:
            log("Adding {} spaces to {}".format(spaces, line))
            new_lines.append(" " * spaces + line)
        return "\n".join(new_lines)

    def add_export(export):
        exports.append(export)

    def add_new_class(class_name):
        new_classes.append(class_name)

    def indent_code(code, indent):
        return add_spaces(code, indent)

    def passthrough_context(result):
        nonlocal set_context_type

        for export in result['exports']:
            add_export(export)
        if "context_type" in result:
            set_context_type = result['context_type']
        for class_name in result['new_classes']:
            add_new_class(class_name)

    for statement in tree:
        log("Generating for " + statement['type'] + " parent context: {}".format(parent_context_type))
        if statement['type'] == TYPES['STATEMENT']:
            if isinstance(statement['statement'], str) or isinstance(statement['statement'], float) or isinstance(statement['statement'], int):
                add_code(str(statement['statement']))
                continue
            result = generate_code(statement['statement'], context)
            add_code(result['code'], 4)
            passthrough_context(result)
        elif statement['type'] == TYPES['VARIABLE_ASSIGNMENT']:
            value = generate_code(statement['value'], context)['code']
            value = remove_spaces(value)
            name = statement['name']
            if isinstance(name, dict):
                name = generate_code(statement['name'], context)['code']
            code = ""
            if value[-1] == ";":
                # we handle the semicolon ourselves
                value = value[:-1]
            # dot cannot be a generated variable
            if name not in context['generated_variables'] and "." not in name:
                code += "let "
                context['generated_variables'].append(name)
            code += name + " = " + value + ";"
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
                child_code = remove_spaces(child_code)
                child_code = add_spaces(child_code, end_spaces + 4)
                add_code(opening_statement + "\n" + child_code + "\n" + " "*end_spaces + "}")
            else:
                add_code(opening_statement + "\n"  + " "*end_spaces + "}")
            passthrough_context(opening_statement_result)
        elif statement['type'] == TYPES['IF']:
            condition_code = generate_code(statement['condition'], context)['code'].lstrip()
            children = generate_code(statement['nested'], context)['code']
            children = remove_spaces(children)
            add_code("if (" + condition_code + ") {")
            if children.strip() != "":
                add_code(children, 4)
            add_code("}")
        elif statement['type'] == TYPES['CONDITION']:
            left_hand = generate_code(statement['left_hand'], context)['code'].lstrip()
            right_hand = generate_code(statement['right_hand'], context)['code'].lstrip()

            add_code(left_hand + " " + statement['condition'] + " " + right_hand)
        elif statement['type'] == TYPES['FOR_OF']:
            children = generate_code(statement['nested'], context)['code']
            children = remove_spaces(children)
            if "key" in statement:
                add_code("for (let " + statement['key'] + ' in ' + statement['variable'] + ") {")
                add_code(" "*4 + "let " + statement['value'] + " = " + statement['variable'] + "[" + statement['key'] + "];")
            else:
                add_code("for (let " + statement['value'] + ' of ' + statement['variable'] + ") {")
            if children.strip() != "":
                add_code(children, 4)
            add_code("}")
        elif statement['type'] == TYPES['FOR']:
            condition_list = []
            for condition_str in statement['conditions']:
                condition_code = generate_code(condition_str, context)['code']
                if condition_code[-1] == ";":
                    condition_code = condition_code[:-1]
                condition_list.append(remove_spaces(condition_code))
            conditions = ";".join(condition_list)
            children = generate_code(statement['nested'], context)['code']
            children = remove_spaces(children)
            add_code("for (" + conditions + ") {\n" + add_spaces(children, 4) + "\n}")
        elif statement['type'] == TYPES['WHILE']:
            condition_code = generate_code(statement['condition'], context)['code']
            children = generate_code(statement['nested'], context)['code']
            add_code("while (" + condition_code + ") {\n" + children + "\n}")
        elif statement['type'] == TYPES['FUNCTION']:
            start = "async "
            children = generate_code(statement['nested'], context)['code']
            log("parent context is {}".format(parent_context_type))
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
            if children.strip() != "":
                add_code(children)
            add_code("}")
        elif statement['type'] == TYPES['CALL_FUNC']:
            new_context = context.copy()
            new_context['spaces'] = 0

            parameter_code = generate_code(statement['parameters'], new_context)['code']
            func_name = generate_code(statement['function'], new_context)['code']\

            code = "await " + remove_spaces(func_name) + "("
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
            new_context = context.copy()
            new_context['parent_type'] = 'class'
            children = generate_code(statement['nested'], new_context)["code"]
            if children != "":
                add_code(children)
            add_code("}")
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
                if child_code[-1] == ";":
                    child_code = child_code[:-1]
                all_child_codes.append(child_code)
            final_child_code = ",\n".join(all_child_codes)
            add_code("[\n" + final_child_code + "\n]")
        elif statement['type'] == TYPES['MAP']:
            all_child_codes = []
            for child in statement['children']:
                child_code = generate_code(child, context)['code']
                child_code = indent_code(remove_spaces(child_code), 4)
                all_child_codes.append(child_code)
            if len(all_child_codes) == 0:
                add_code("{};")
            else:
                final_child_code = ",\n".join(all_child_codes)
                add_code("{\n" + final_child_code + "\n};")
        elif statement['type'] == TYPES["MAP_ROW"]:
            value_code = generate_code(statement['value'], context)['code']
            add_code("\"" + statement['key'] + "\": " + remove_spaces(value_code))
        elif statement['type'] == TYPES["JSX_START_TAG"]:
            code = ""
            if statement['tag'] in context['generated_classes']:
                code += "new " + statement['tag'] + "({"
            else:
                code += "new Component(\"" + statement['tag'] + "\", {"

            all_attributes = []
            for attribute in statement['attributes']:
                attribute_code = generate_code(attribute, context)['code']
                attribute_code = remove_spaces(attribute_code)
                attribute_code = indent_code(attribute_code, 4)
                all_attributes.append(attribute_code)
            if len(all_attributes) > 0:
                code += "\n" + ",\n".join(all_attributes) + "\n"

            code += "}, ["

            code += "]);"
            add_code(code)
        elif statement['type'] == TYPES['JSX_ATTRIBUTE']:
            right_hand_code = generate_code(statement['right_hand'], context)['code']
            right_hand_code = remove_spaces(right_hand_code)
            add_code("\"" + statement['name'] + "\": " + right_hand_code)
        elif statement['type'] == TYPES['RETURN']:
            value_result = generate_code(statement['value'], context)
            passthrough_context(value_result)
            value_code = value_result['code']
            value_code = remove_spaces(value_code)
            if value_code[-1] == ";":
                value_code = value_code[:-1]

            add_code("return " + value_code + ";")
        elif statement['type'] == TYPES["VALUE_MANIPULATION"]:
            value_code = []
            for value in statement['values']:
                if isinstance(value, str):
                    value_code.append(value)
                else:
                    result = generate_code(value, context)
                    passthrough_context(result)
                    result_code = result['code']
                    if result_code[-1] == ";":
                        result_code = result_code[:-1]
                    result_code = remove_spaces(result_code)
                    value_code.append(result_code)
            add_code(" ".join(value_code) + ";")
        elif statement['type'] == TYPES["ELSE"]:
            add_code("else {")
            children = generate_code(statement['nested'], context)['code']
            if children.strip() != "":
                add_code(children)
            add_code("}")
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